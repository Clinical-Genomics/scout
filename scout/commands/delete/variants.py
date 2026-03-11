from typing import List, Optional, Tuple

import click
from flask import current_app, url_for
from flask.cli import with_appcontext

from scout.adapter.mongo import MongoAdapter
from scout.constants import ANALYSIS_TYPES, CASE_STATUSES, VARIANTS_TARGET_FROM_CATEGORY
from scout.server.extensions import store

BYTES_IN_ONE_GIGABYTE = 1073741824
DELETE_VARIANTS_HEADER = [
    "Case n.",
    "Ncases",
    "Institute",
    "Case name",
    "Case ID",
    "Case track",
    "Analysis date",
    "Status",
    "Research",
    "Total variants",
    "Removed variants",
]
VARIANT_CATEGORIES = list(VARIANTS_TARGET_FROM_CATEGORY.keys())


def _set_keep_ctg(keep_ctg: Tuple[str], rm_ctg: Tuple[str]) -> List[str]:
    """Define the categories of variants that should not be removed."""
    if keep_ctg and rm_ctg:
        raise click.UsageError("Please use either '--keep-ctg' or '--rm-ctg', not both.")
    if keep_ctg:
        return list(keep_ctg)
    if rm_ctg:
        return list(set(VARIANT_CATEGORIES).difference(set(rm_ctg)))
    return []


def get_case_ids(case_file: Optional[str], case_id: List[str]) -> List[str]:
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


def handle_delete_variants(
    store: MongoAdapter, keep_ctg: List[str], dry_run: bool, variants_query: dict
) -> Tuple[int]:
    """Handle variant removal for a case or count how many variants would be removed if it's a simulation.."""

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
    case_id: tuple,
    case_file: str,
    institute: str,
    status: tuple,
    older_than: int,
    analysis_type: tuple,
    rank_threshold: int,
    variants_threshold: int,
    rm_ctg: tuple,
    keep_ctg: tuple,
    dry_run: bool,
) -> None:
    """Delete variants for one or more cases"""

    user_obj = store.user(user)
    if user_obj is None:
        click.echo(f"Could not find a user with email '{user}' in database")
        return

    case_ids = get_case_ids(case_file=case_file, case_id=case_id)

    total_deleted = 0

    if dry_run:
        click.echo("--------------- DRY RUN COMMAND ---------------")
        items_name = "estimated deleted variants"
    else:
        click.confirm("Variants are going to be deleted from database. Continue?", abort=True)
        items_name = "deleted variants"

    case_query = store.build_case_query(
        case_ids=case_ids,
        institute_id=institute,
        status=status,
        older_than=older_than,
        analysis_type=analysis_type,
    )
    # Estimate the average size of a variant document in database
    avg_var_size = store.collection_stats("variant").get("avgObjSize", 0)  # in bytes

    # Get all cases where case_query applies
    n_cases = store.case_collection.count_documents(case_query)
    cases = store.cases(query=case_query)
    filters = (
        f"Rank-score threshold:{rank_threshold}, case n. variants threshold:{variants_threshold}."
    )
    click.echo("\t".join(DELETE_VARIANTS_HEADER))
    keep_ctg = _set_keep_ctg(keep_ctg=keep_ctg, rm_ctg=rm_ctg)

    for nr, case in enumerate(cases, 1):

        case_id = case["_id"]
        institute_id = case["owner"]
        case_n_variants = store.variant_collection.count_documents(
            {"case_id": case_id}
        ) + store.omics_variant_collection.count_documents({"case_id": case_id})
        # Skip case if user provided a number of variants to keep and this number is less than total number of case variants
        if variants_threshold and case_n_variants < variants_threshold:
            continue
        # Get evaluated variants for the case that haven't been dismissed
        case_evaluated, _ = store.evaluated_variants(case_id=case_id, institute_id=institute_id)
        evaluated_not_dismissed = [
            variant["_id"] for variant in case_evaluated if "dismiss_variant" not in variant
        ]
        # Do not remove variants that are either pinned, causative or evaluated not dismissed
        variants_to_keep = (
            case.get("suspects", []) + case.get("causatives", []) + evaluated_not_dismissed or []
        )

        variants_query: dict = store.delete_variants_query(
            case_id, variants_to_keep, rank_threshold, keep_ctg
        )

        remove_n_variants, remove_n_omics_variants = handle_delete_variants(
            store=store, keep_ctg=keep_ctg, dry_run=dry_run, variants_query=variants_query
        )
        total_deleted += remove_n_variants + remove_n_omics_variants
        click.echo(
            "\t".join(
                [
                    str(nr),
                    str(n_cases),
                    case["owner"],
                    case["display_name"],
                    case_id,
                    case.get("track", ""),
                    str(case["analysis_date"]),
                    case.get("status", ""),
                    str(case.get("is_research", "")),
                    str(case_n_variants),
                    str(remove_n_variants + remove_n_omics_variants),
                ]
            )
        )

        if dry_run:  # Do not create an associated event
            continue

        # Create event in database
        institute_obj = store.institute(case["owner"])
        with current_app.test_request_context("/cases"):
            url = url_for(
                "cases.case",
                institute_id=institute_obj["_id"],
                case_name=case["display_name"],
            )
            store.remove_variants_event(
                institute=institute_obj,
                case=case,
                user=user_obj,
                link=url,
                content=filters,
            )

        # Update case variants count
        store.case_variants_count(case_id, institute_obj["_id"], True)

    click.echo(f"Total {items_name}: {total_deleted}")
    click.echo(
        f"Estimated space freed (GB): {round((total_deleted * avg_var_size) / BYTES_IN_ONE_GIGABYTE, 4)}"
    )
