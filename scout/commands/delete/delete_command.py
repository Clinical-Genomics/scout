import logging

import click
from flask import current_app, url_for
from flask.cli import with_appcontext

from scout.commands.delete.variants import variants
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


CASE_RNA_KEYS = [
    "RNAfusion_inspector",
    "RNAfusion_inspector_research",
    "RNAfusion_report",
    "RNAfusion_report_research",
    "gene_fusion_report",
    "gene_fusion_report_research",
    "has_outliers",
    "multiqc_rna",
    "omics_files",
    "rna_delivery_report",
    "rna_genome_build",
]
INDIVIDUAL_RNA_KEYS = [
    "omics_sample_id",
    "rna_alignment_path",
    "rna_coverage_bigwig",
    "splice_junctions_bed",
]


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
        click.echo("Couldn't find any case in database matching the provided parameters.")
        raise click.Abort()

    LOG.info("Running deleting case {0}".format(case_id))
    case = adapter.delete_case(case_id=case_obj["_id"])

    adapter.delete_variants(case_id=case_obj["_id"], variant_type="clinical")
    adapter.delete_variants(case_id=case_obj["_id"], variant_type="research")
    adapter.delete_omics_variants_by_category(case_id=case_obj["_id"], variant_type="clinical")
    adapter.delete_omics_variants_by_category(case_id=case_obj["_id"], variant_type="research")


@click.command("rna", short_help="Remove all RNA data from a case")
@click.option("-c", "--case-id", required=True)
@click.option("--yes", "-y", is_flag=True, help="Automatically confirm and do not prompt.")
def rna(case_id, yes):
    """
    Delete all RNA-associated data from a case. This removes RNA information from the case document and related variants.
    The case document will not show any signs of having been modified,
    and no history of these changes will be recorded.
    This command is intended to be used when something has gone wrong and incorrect RNA data has been loaded for a case.
    """
    adapter = store
    case_obj = adapter.case(case_id=case_id)
    if not case_obj:
        click.echo(f"Couldn't find any case in database with ID {case_id}.")
        raise click.Abort()

    if not yes:
        click.confirm(
            "This will permanently delete all RNA-related data from the case. Continue?",
            abort=True,
        )
    removed_keys = set()

    # Remove case-level associated key/values
    for key in CASE_RNA_KEYS:
        if key not in case_obj:
            continue
        removed_keys.add(key)
        case_obj.pop(key, None)

    # Remove individual-level associated key/values
    for ind in case_obj.get("individuals", []):
        for key in INDIVIDUAL_RNA_KEYS:
            if key not in ind:
                continue
            removed_keys.add(f"individual.{key}")
            ind.pop(key)

    adapter.case_collection.find_one_and_replace(
        {"_id": case_obj["_id"]},
        case_obj,
    )

    click.echo(
        f"Updated/removed keys: {', '.join(sorted(removed_keys))}"
        if removed_keys
        else "No matching RNA keys found."
    )

    # Remove outliers variants
    deleted_count = store.omics_variant_collection.delete_many(
        {
            "case_id": case_id,
            "sub_category": {"$in": ["splicing", "expression"]},
        }
    ).deleted_count
    click.echo(f"Deleted {deleted_count} omics variant documents for case {case_id}.")

    # Update variants count in case document
    adapter.case_variants_count(case_id, case_obj["owner"], True)


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
delete.add_command(rna)
delete.add_command(variants)
