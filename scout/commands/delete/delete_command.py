import logging
from typing import List, Optional, Tuple

import click
from flask import current_app, url_for
from flask.cli import with_appcontext

from scout.adapter.mongo import MongoAdapter
from scout.constants import ANALYSIS_TYPES, CASE_STATUSES, VARIANTS_TARGET_FROM_CATEGORY
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

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
        case_evaluated = store.evaluated_variants(case_id=case_id, institute_id=institute_id)
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


@click.command("panel", short_help="Delete a gene panel")
@click.option("--panel-id", help="The panel identifier name", required=True)
@click.option("-v", "--version", type=float)
@with_appcontext
def panel(panel_id, version):
    """Delete a version of a gene panel or all versions of a gene panel"""
    LOG.info("Running scout delete panel")
    adapter = store

    res = adapter.gene_panels(panel_id=panel_id, version=version)
    panel_objs = [panel_obj for panel_obj in res]
    if len(panel_objs) == 0:
        LOG.info("No panels found")

    for panel_obj in panel_objs:
        adapter.delete_panel(panel_obj)


@click.command("index", short_help="Delete all indexes")
@with_appcontext
def index():
    """Delete all indexes in the database"""
    LOG.info("Running scout delete index")
    adapter = store

    for collection in adapter.db.list_collection_names():
        adapter.db[collection].drop_indexes()
    LOG.info("All indexes deleted")


@click.command("user", short_help="Delete a user")
@click.option("-m", "--mail", required=True)
@with_appcontext
def user(mail):
    """Delete a user from the database"""
    LOG.info("Running scout delete user")
    adapter = store
    user_obj = adapter.user(mail)
    if not user_obj:
        LOG.warning("User {0} could not be found in database".format(mail))
        return

    # Check if user has associated MatchMaker Exchange submissions
    mme_submitted_cases = adapter.user_mme_submissions(user_obj)
    if mme_submitted_cases:
        click.confirm(
            f"User can't be removed because MatchMaker Exchange submissions (n. cases={len(mme_submitted_cases)}) are associated to it. Reassign patients to another user?",
            abort=True,
        )
        new_contact_email = click.prompt(
            "Assign patients to user with email",
            type=str,
        )
        try:
            adapter.mme_reassign(mme_submitted_cases, new_contact_email)
        except Exception as ex:
            LOG.error(ex)
            return

    result = adapter.delete_user(mail)
    if result.deleted_count == 0:
        return
    click.echo(f"User was correctly removed from database.")
    # remove this user as assignee from any case where it is found
    assigned_cases = adapter.cases(assignee=mail)
    updated_cases = 0
    with current_app.test_request_context("/cases"):
        for case_obj in assigned_cases:
            institute_obj = adapter.institute(case_obj["owner"])
            link = url_for(
                "cases.case",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
            )
            inactivate_case = case_obj.get("status", "active") == "active" and case_obj[
                "assignees"
            ] == [mail]
            if adapter.unassign(institute_obj, case_obj, user_obj, link, inactivate_case):
                updated_cases += 1
    click.echo(f"User was removed as assignee from {updated_cases} case(s).")


@click.command("genes", short_help="Delete genes")
@click.option("-b", "build", type=click.Choice(["37", "38"]))
@with_appcontext
def genes(build):
    """Delete all genes in the database"""
    LOG.info("Running scout delete genes")
    adapter = store

    if build:
        LOG.info("Dropping genes collection for build: %s", build)
    else:
        LOG.info("Dropping all genes")
    adapter.drop_genes(build=build)


@click.command("exons", short_help="Delete exons")
@click.option("-b", "build", type=click.Choice(["37", "38"]))
@with_appcontext
def exons(build):
    """Delete all exons in the database"""
    LOG.info("Running scout delete exons")
    adapter = store

    adapter.drop_exons(build)


@click.command("case", short_help="Delete a case")
@click.option("-i", "--institute", help="institute id of related cases")
@click.option("-c", "--case-id")
@click.option("-d", "--display-name")
@with_appcontext
def case(institute, case_id, display_name):
    """Delete a case and it's variants from the database"""
    adapter = store
    case_obj = None

    if not (case_id or display_name):
        click.echo("Please specify what case to delete")
        raise click.Abort()

    if display_name:
        if not institute:
            click.echo(
                "Please specify the owner of the case that should be "
                "deleted with flag '-i/--institute'."
            )
            raise click.Abort()
        case_obj = adapter.case(display_name=display_name, institute_id=institute)
    else:
        case_obj = adapter.case(case_id=case_id)

    if not case_obj:
        click.echo("Coudn't find any case in database matching the provided parameters.")
        raise click.Abort()

    LOG.info("Running deleting case {0}".format(case_id))
    case = adapter.delete_case(case_id=case_obj["_id"])

    adapter.delete_variants(case_id=case_obj["_id"], variant_type="clinical")
    adapter.delete_variants(case_id=case_obj["_id"], variant_type="research")


# @click.command('diseases', short_help='Display all diseases')
# @click.pass_context
# def diseases(context):
#     """Show all diseases in the database"""
#     LOG.info("Running scout view diseases")
#     adapter = context.obj['adapter']
#
#     click.echo("Disease")
#     for disease_obj in adapter.disease_terms():
#         click.echo("{0}:{1}".format(
#             disease_obj['source'],
#             disease_obj['disease_id'],
#         ))
#
# @click.command('hpo', short_help='Display all hpo terms')
# @click.pass_context
# def hpo(context):
#     """Show all hpo terms in the database"""
#     LOG.info("Running scout view hpo")
#     adapter = context.obj['adapter']
#
#     click.echo("hpo_id\tdescription")
#     for hpo_obj in adapter.hpo_terms():
#         click.echo("{0}\t{1}".format(
#             hpo_obj.hpo_id,
#             hpo_obj.description,
#         ))


@click.group()
def delete():
    """
    Delete objects from the database.
    """


delete.add_command(panel)
delete.add_command(genes)
delete.add_command(case)
delete.add_command(user)
delete.add_command(index)
delete.add_command(exons)
delete.add_command(variants)
