import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("case", short_help="Delete a case")
@click.option("-i", "--institute", help="institute id of related cases")
@click.option("-c", "--case-id")
@click.option("-d", "--display-name")
@with_appcontext
def case(institute, case_id, display_name):
    """Delete a case and it's variants from the database"""
    adapter = store

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
    adapter.delete_case(case_id=case_obj["_id"])

    adapter.delete_variants(case_id=case_obj["_id"], variant_type="clinical")
    adapter.delete_variants(case_id=case_obj["_id"], variant_type="research")
    adapter.delete_omics_variants_by_category(case_id=case_obj["_id"], variant_type="clinical")
    adapter.delete_omics_variants_by_category(case_id=case_obj["_id"], variant_type="research")
