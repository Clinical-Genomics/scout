import logging
from typing import Dict, Iterable, List, Optional, Tuple

import click
from flask import current_app, url_for
from flask.cli import with_appcontext

from scout.adapter import MongoAdapter
from scout.constants import ANALYSIS_TYPES, CASE_STATUSES, VARIANTS_TARGET_FROM_CATEGORY
from scout.server.extensions import store

delete_stats = {"case_counter": 0, "deleted_variant_counter": 0, "deleted_outlier_counter": 0}
LOG = logging.getLogger(__name__)
DELETE_VARIANTS_HEADER = [
    "Case n.",
    "Institute",
    "Case name",
    "Case ID",
    "Case track",
    "Analysis date",
    "Status",
    "Research",
    "DNA variants",
    "Removed DNA variants",
    "Removed Outlier variants",
]
VARIANT_CATEGORIES = list(VARIANTS_TARGET_FROM_CATEGORY.keys())


def handle_delete_variants(
    store: MongoAdapter,
    keep_ctg: List[str],
    dry_run: bool,
    variants_query: dict,
) -> Tuple[int, int]:
    """
    Handle variant removal for a case.

    If dry_run is True, counts how many variants *would be removed* without deleting.
    Returns a tuple: (number_deleted_variants, number_deleted_omics_variants)
    """

    if dry_run:
        remove_n_variants = store.variant_collection.count_documents(variants_query)
        remove_n_omics_variants = (
            store.omics_variant_collection.count_documents(variants_query)
            if "outlier" not in keep_ctg
            else 0
        )
    else:
        remove_n_variants = store.variant_collection.delete_many(variants_query).deleted_count
        remove_n_omics_variants = (
            store.omics_variant_collection.delete_many(variants_query).deleted_count
            if "outlier" not in keep_ctg
            else 0
        )

    return remove_n_variants, remove_n_omics_variants


def _create_delete_variants_event(
    user_obj: dict,
    institute_id: str,
    display_name: str,
    rank_threshold: int,
    variants_threshold: Optional[int],
) -> None:
    institute_obj = store.institute(institute_id)
    with current_app.test_request_context("/cases"):
        url = url_for(
            "cases.case",
            institute_id=institute_obj["_id"],
            case_name=display_name,
        )

        threshold_parts: List[str] = []
        threshold_parts.append(f"Rank-score threshold:{rank_threshold}")
        if variants_threshold is not None:
            threshold_parts.append(f"case n. variants threshold:{variants_threshold}")
        content_str = ", ".join(threshold_parts)

        store.remove_variants_event(
            institute=institute_obj,
            case=store.case(case_id=case_id),
            user=user_obj,
            link=url,
            content=content_str,
        )


def _process_cases(
    cases: List[dict],
    user_obj: Dict,
    rank_threshold: int | None,
    variants_threshold: int | None,
    keep_ctg: Iterable[str],
    dry_run: bool,
) -> None:
    """
    Process removing variants from cases, deleting variants using handle_delete_variants.

    - Keeps suspects/causatives/evaluated-not-dismissed variants
    - Supports rank_threshold and variants_threshold
    - Supports dry-run
    - Creates events and updates variant counts per case
    """

    pipeline = [
        {"$group": {"_id": "$case_id", "variant_count": {"$sum": 1}}},
        {
            "$lookup": {
                "from": "case",
                "localField": "_id",
                "foreignField": "_id",
                "as": "case_info",
            }
        },
        {"$unwind": "$case_info"},
        {
            "$project": {
                "_id": 1,
                "variant_count": 1,
                "display_name": "$case_info.display_name",
                "owner": "$case_info.owner",
                "analysis_date": "$case_info.analysis_date",
                "suspects": "$case_info.suspects",
                "causatives": "$case_info.causatives",
            }
        },
        {"$sort": {"variant_count": -1}},
    ]

    for doc in store.variant_collection.aggregate(pipeline, allowDiskUse=True):
        if cases and doc not in cases:
            continue
        if variants_threshold and doc["variant_count"] < variants_threshold:
            continue

        delete_stats["case_counter"] += 1

        case_evaluated, _ = store.evaluated_variants(case_id=doc["_id"], institute_id=doc["owner"])
        evaluated_not_dismissed = [v["_id"] for v in case_evaluated if "dismiss_variant" not in v]
        variants_to_keep = (
            doc.get("suspects", []) + doc.get("causatives", []) + evaluated_not_dismissed
        )

        variants_query: dict = store.delete_variants_query(
            case_id=doc["_id"],
            variants_to_keep=variants_to_keep,
            min_rank_threshold=rank_threshold,
            keep_ctg=keep_ctg,
        )

        removed_variants, removed_omics_variants = handle_delete_variants(
            store=store,
            keep_ctg=list(keep_ctg),
            dry_run=dry_run,
            variants_query=variants_query,
        )

        delete_stats["deleted_variant_counter"] += removed_variants
        delete_stats["deleted_outlier_counter"] += removed_omics_variants

        click.echo(
            f"{delete_stats['case_counter']}\t{doc['_id']}\t{doc['owner']}\t{doc['display_name']}\t{doc.get('analysis_date')}\t{doc['variant_count']}\t{removed_variants}\t{removed_omics_variants}"
        )

        if dry_run:
            return

        _create_delete_variants_event(
            user_obj=user_obj,
            case_id=doc["_id"],
            institute_id=doc["owner"],
            display_name=doc["display_name"],
            rank_threshold=rank_threshold,
            variants_threshold=variants_threshold,
        )

        # Update case variant count
        store.case_variants_count(doc["_id"], doc["owner"], True)


def get_case_ids(case_file: Optional[str], case_id: Optional[List[str]]) -> List[str]:
    """Fetch the _id of the cases to remove variants from."""
    if case_file and case_id:
        click.echo(
            "You should specify either case ID (multiple times if needed) or the path to a text file containing a list of case IDs (one per line)."
        )
        return []
    return (
        [line.strip() for line in open(case_file).readlines() if line.strip()]
        if case_file
        else list(case_id)
    )


def _set_keep_ctg(
    keep_ctg: Optional[Tuple[str, ...]], rm_ctg: Optional[Tuple[str, ...]]
) -> List[str]:
    """Define the categories of variants that should not be removed."""
    if keep_ctg and rm_ctg:
        raise click.UsageError("Please use either '--keep-ctg' or '--rm-ctg', not both.")
    if keep_ctg:
        return list(keep_ctg)
    if rm_ctg:
        return list(set(VARIANT_CATEGORIES).difference(set(rm_ctg)))
    return []


@click.command("variants", short_help="Delete variants for one or more cases")
@click.option("-u", "--user", help="User running this command (email)", required=True)
@click.option("-c", "--case-id", help="Case id", multiple=True)
@click.option(
    "-f",
    "--case-file",
    help="Path to file containing list of case IDs",
    type=click.Path(exists=True),
)
@click.option("-i", "--institute", help="Restrict to cases with specified institute ID")
@click.option(
    "--status",
    type=click.Choice(CASE_STATUSES),
    multiple=True,
    default=[],
    help="Restrict to cases with specified status",
)
@click.option("--older-than", type=click.INT, default=0, help="Older than (months)")
@click.option(
    "--analysis-type",
    type=click.Choice(ANALYSIS_TYPES),
    multiple=True,
    help="Type of analysis",
)
@click.option("--rank-threshold", type=click.INT, default=5, help="With rank threshold lower than")
@click.option("--variants-threshold", type=click.INT, help="With more variants than")
@click.option(
    "--rm-ctg",
    type=click.Choice(VARIANT_CATEGORIES),
    multiple=True,
    required=False,
    help="Remove only the following categories",
)
@click.option(
    "--keep-ctg",
    type=click.Choice(VARIANT_CATEGORIES),
    multiple=True,
    required=False,
    help="Keep the following categories",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a simulation without removing any variant",
)
@with_appcontext
def variants(
    user: str,
    rank_threshold: int,
    case_id: Optional[Tuple[str, ...]] = None,
    case_file: Optional[str] = None,
    institute: Optional[str] = None,
    status: Optional[Tuple[str, ...]] = None,
    older_than: Optional[int] = None,
    analysis_type: Optional[Tuple[str, ...]] = None,
    variants_threshold: Optional[int] = None,
    rm_ctg: Optional[Tuple[str, ...]] = None,
    keep_ctg: Optional[Tuple[str, ...]] = None,
    dry_run: bool = False,
) -> None:
    """Delete variants for one or more cases"""

    user_obj = store.user(user)
    if user_obj is None:
        click.echo(f"Could not find a user with email '{user}' in database")
        return

    case_ids = get_case_ids(case_file=case_file, case_id=case_id)

    if dry_run:
        click.echo("--------------- DRY RUN COMMAND ---------------")
        items_name = "estimated deleted variants"
    else:
        click.confirm(
            "Variants are going to be deleted from database. Continue?",
            abort=True,
        )
        items_name = "deleted variants"

    keep_ctg = _set_keep_ctg(keep_ctg=keep_ctg, rm_ctg=rm_ctg)
    click.echo("\t".join(DELETE_VARIANTS_HEADER))
    _process_cases(
        cases=case_ids,
        user_obj=user_obj,
        rank_threshold=rank_threshold,
        variants_threshold=variants_threshold,
        keep_ctg=keep_ctg,
        dry_run=dry_run,
    )
    click.echo(
        f"Total {items_name}: {delete_stats['deleted_variant_counter'] + delete_stats['deleted_outlier_counter']}"
    )
