import logging
from typing import Dict, Iterable, List, Optional, Tuple

import click
from flask import current_app, url_for
from flask.cli import with_appcontext
from pymongo import DeleteMany

from scout.constants import ANALYSIS_TYPES, CASE_STATUSES, VARIANTS_TARGET_FROM_CATEGORY
from scout.server.extensions import store

BATCH_SIZE = 100
LOG = logging.getLogger(__name__)
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


def _log_case(cases: List[Dict], cid: str, deleted_n: int) -> None:
    """Log deletion information for a single case."""

    case = next(c for c in cases if c["_id"] == cid)

    click.echo(
        "\t".join(
            [
                case["owner"],
                case["display_name"],
                str(cid),
                str(case.get("analysis_date", "")),
                str(case.get("status", "")),
                str(deleted_n),
            ]
        )
    )


def _process_batch(
    cases: List[Dict[str, Any]],
    user_obj: Dict[str, Any],
    rank_threshold: int | None,
    variants_threshold: int | None,
    keep_ctg: Iterable[str],
    dry_run: bool,
) -> int:
    """
    Process a batch of cases by performing bulk deletion of variants.

    Creates events with threshold info, respecting optional thresholds.
    """

    total_deleted: int = 0
    case_ids: List[Any] = [case["_id"] for case in cases]

    # Optional variant count pre-computation
    counts: Dict[Any, int] = {}
    if variants_threshold is not None:
        pipeline = [
            {"$match": {"case_id": {"$in": case_ids}}},
            {"$group": {"_id": "$case_id", "n": {"$sum": 1}}},
        ]
        for doc in store.variant_collection.aggregate(pipeline, allowDiskUse=True):
            counts[doc["_id"]] = doc["n"]

    delete_ops: List[DeleteMany] = []
    case_delete_map: Dict[Any, Dict[str, Any]] = {}

    for case in cases:
        cid = case["_id"]

        # Skip case if variants_threshold is set
        if variants_threshold is not None and counts.get(cid, 0) < variants_threshold:
            continue

        delete_query: Dict[str, Any] = {
            "case_id": cid,
            "category": {"$nin": list(keep_ctg)},
        }
        if rank_threshold is not None:
            delete_query["rank_score"] = {"$lt": rank_threshold}

        delete_ops.append(DeleteMany(delete_query))
        case_delete_map[cid] = delete_query

    if not delete_ops:
        return 0

    # Dry-run mode
    if dry_run:
        for cid, query in case_delete_map.items():
            n: int = store.variant_collection.count_documents(query)
            total_deleted += n
        return total_deleted

    # Execute bulk delete
    result: BulkWriteResult = store.variant_collection.bulk_write(
        delete_ops,
        ordered=False,
    )
    total_deleted += result.deleted_count

    # Post-delete operations: events + variant count updates
    for case in cases:
        cid = case["_id"]
        if cid not in case_delete_map:
            continue

        institute_obj: Dict[str, Any] = store.institute(case["owner"])

        with current_app.test_request_context("/cases"):
            url: str = url_for(
                "cases.case",
                institute_id=institute_obj["_id"],
                case_name=case["display_name"],
            )

            # -----------------------------
            # Build event content string
            # -----------------------------
            threshold_parts: List[str] = []
            if rank_threshold is not None:
                threshold_parts.append(f"Rank-score threshold:{rank_threshold}")
            if variants_threshold is not None:
                threshold_parts.append(f"case n. variants threshold:{variants_threshold}")

            content_str: str = ", ".join(threshold_parts)

            store.remove_variants_event(
                institute=institute_obj,
                case=case,
                user=user_obj,
                link=url,
                content=content_str,
            )

        store.case_variants_count(cid, institute_obj["_id"], True)

    return total_deleted


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
    case_id: Optional[Tuple[str, ...]] = None,
    case_file: Optional[str] = None,
    institute: Optional[str] = None,
    status: Optional[Tuple[str, ...]] = None,
    older_than: Optional[int] = None,
    analysis_type: Optional[Tuple[str, ...]] = None,
    rank_threshold: Optional[int] = None,
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

    case_query = store.build_case_query(
        case_ids=case_ids,
        institute_id=institute,
        status=status,
        older_than=older_than,
        analysis_type=analysis_type,
    )

    keep_ctg = _set_keep_ctg(keep_ctg=keep_ctg, rm_ctg=rm_ctg)

    # Stream minimal case info
    cases_cursor = store.case_collection.find(
        case_query,
        projection={
            "_id": 1,
            "owner": 1,
            "display_name": 1,
            "analysis_date": 1,
            "status": 1,
            "is_research": 1,
            "track": 1,
        },
        batch_size=50,
    )

    total_deleted = 0
    batch = []

    click.echo("\t".join(DELETE_VARIANTS_HEADER))

    for case in cases_cursor:
        batch.append(case)

        if len(batch) >= BATCH_SIZE:
            total_deleted += _process_batch(
                batch,
                user_obj,
                rank_threshold,
                variants_threshold,
                keep_ctg,
                dry_run,
            )
            batch.clear()

    if batch:
        total_deleted += _process_batch(
            batch,
            user_obj,
            rank_threshold,
            variants_threshold,
            keep_ctg,
            dry_run,
        )

    click.echo(f"Total {items_name}: {total_deleted}")
