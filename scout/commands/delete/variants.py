import logging
from typing import List, Optional, Tuple

import click
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
    cases: List[dict],
    user_obj: dict,
    rank_threshold: int,
    variants_threshold: int,
    keep_ctg: Iterable[str],
    dry_run: bool,
) -> int:
    """Process a batch of cases by performing bulk deletion of variants.
    Returns total number of deleted (or estimated deleted) variants.
    """
    total_deleted = 0
    case_ids = [case["_id"] for case in cases]

    # ---- OPTIONAL: pre-count variants for threshold ----
    counts = {}
    if variants_threshold:
        pipeline = [
            {"$match": {"case_id": {"$in": case_ids}}},
            {"$group": {"_id": "$case_id", "n": {"$sum": 1}}},
        ]

        for doc in store.variant_collection.aggregate(pipeline, allowDiskUse=True):
            counts[doc["_id"]] = doc["n"]

    delete_ops = []
    case_delete_map = {}

    for case in cases:
        cid = case["_id"]

        if variants_threshold and counts.get(cid, 0) < variants_threshold:
            continue

        # Positive delete filter only
        delete_query = {
            "case_id": cid,
            "rank_score": {"$lt": rank_threshold},
            "category": {"$nin": keep_ctg},
        }

        delete_ops.append(DeleteMany(delete_query))
        case_delete_map[cid] = delete_query

    if not delete_ops:
        return 0

    # ---- DRY RUN ----
    if dry_run:
        for cid, query in case_delete_map.items():
            n = store.variant_collection.count_documents(query)
            total_deleted += n
            _log_case(cases, cid, n)
        return total_deleted

    # ---- REAL DELETE ----
    result = store.variant_collection.bulk_write(delete_ops, ordered=False)

    total_deleted += result.deleted_count

    # ---- Post-delete: events + count update ----
    for case in cases:
        cid = case["_id"]

        if cid not in case_delete_map:
            continue

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
                content=f"Rank-score threshold:{rank_threshold}",
            )

        store.case_variants_count(cid, institute_obj["_id"], True)

    return total_deleted


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


def _set_keep_ctg(keep_ctg: Tuple[str], rm_ctg: Tuple[str]) -> List[str]:
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
