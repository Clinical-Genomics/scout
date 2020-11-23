import logging

import click
from datetime import datetime, timedelta
from flask import url_for, current_app
from flask.cli import with_appcontext
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("variants", short_help="Delete variants for one or more cases")
@click.option("-c", "--case-id", help="Case id")
@click.option(
    "-status",
    type=click.Choice(["solved", "archived", "migrated", "active", "inactive", "prioritized"]),
    multiple=True,
    default=["solved", "archived", "migrated"],
    help="Restrict to cases with specified status",
)
@click.option("-older-than", type=click.INT, default=0, help="Older than (months)")
@click.option(
    "-min_rank-threshold", type=click.INT, default=5, help="With rank threshold lower than"
)
@click.option("-variants-threshold", type=click.INT, help="With more variants than")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a simulation without removing any variant",
)
@with_appcontext
def variants(
    case_id,
    status,
    older_than,
    min_rank_threshold,
    variants_threshold,
    dry_run,
):
    """Delete variants for one or more cases"""
    total_deleted = 0
    if dry_run:
        click.echo("--------------- DRY RUN COMMAND ---------------")
    else:
        click.confirm("Variants are going to be deleted from database. Continue?", abort=True)

    case_query = {}
    if case_id:
        case_query["_id"]
    else:
        if status:
            case_query["status"] = {"$in": list(status)}
        if older_than:
            older_than_date = datetime.now() - timedelta(weeks=older_than * 4)  # 4 weeks in a month
            case_query["analysis_date"] = {"$lt": older_than_date}

    # Estimate the average size of a variant document in database
    avg_var_size = store.collection_stats("variant")["avgObjSize"]  # in bytes

    # Get all cases where case_query applies
    n_cases = store.case_collection.count_documents(case_query)
    cases = store.cases(query=case_query)
    for nr, case in enumerate(cases, 1):
        case_id = case["_id"]
        case_n_variants = store.variant_collection.count_documents({"case_id": case_id})
        # Skip case if user provided a number of variants to keep and this number is less than total number of case variants
        if variants_threshold and case_n_variants < variants_threshold:
            # click.echo(f'Skipping case {case["display_name"]} ({case["_id"]}) --> has less variants than {variants_threshold}')
            continue
        click.echo(f"#### {nr}/{n_cases} ###### {case['display_name']} ({case_id})")
        # Get evaluated variants for the case that haven't been dismissed
        case_evaluated = store.evaluated_variants(case_id=case_id)
        evaluated_not_dismissed = [
            variant["_id"] for variant in case_evaluated if "dismiss_variant" not in variant
        ]
        # Do not remove variants that are either pinned, causative or evaluated not dismissed
        variants_to_keep = (
            case.get("suspects", []) + case.get("causatives", []) + evaluated_not_dismissed or []
        )
        variants_query = {}
        case_subquery = {"case_id": case_id}
        # Create query to delete all variants that shouldn't be kept of with rank higher than min_rank_threshold
        if variants_to_keep or min_rank_threshold:
            variants_query["$and"] = [case_subquery]
            if variants_to_keep:
                variants_query["$and"].append({"_id": {"$nin": variants_to_keep}})
            if min_rank_threshold:
                variants_query["$and"].append({"rank_score": {"$lt": min_rank_threshold}})
        else:
            variants_query = case_subquery

        if dry_run:
            # Just print how many variants would be removed for this case
            remove_n_variants = store.variant_collection.count_documents(variants_query)
            total_deleted += remove_n_variants
            click.echo(f"Remove {remove_n_variants} / {case_n_variants} total variants")
            continue

        # delete variants specified by variants_query
        result = store.variant_collection.delete_many(variants_query)
        click.echo(f"Deleted {result.deleted_count} / {case_n_variants} total variants")
        total_deleted += result.deleted_count

    items_name = "deleted variants" or "estimated deleted variants" if dry_run
    click.echo(f"Total {items_name}: {total_deleted}")
    click.echo(f"Estimated space freed (GB): {total_deleted * avg_var_size/1073741824}")


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
                "cases.case", institute_id=institute_obj["_id"], case_name=case_obj["display_name"]
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
    pass


delete.add_command(panel)
delete.add_command(genes)
delete.add_command(case)
delete.add_command(user)
delete.add_command(index)
delete.add_command(exons)
delete.add_command(variants)
