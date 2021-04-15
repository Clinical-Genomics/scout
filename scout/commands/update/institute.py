import logging
from pprint import pprint as pp

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("institute", short_help="Update institute for a case")
@click.argument("institute-id")
@click.option(
    "-c",
    "--coverage-cutoff",
    type=int,
    help="Set a new coverage cutoff for a institute",
)
@click.option(
    "-f",
    "--frequency-cutoff",
    type=float,
    help="Set a new frequency cutoff for a institute",
)
@click.option(
    "-s",
    "--sanger-recipient",
    help="Specify email adress for a existing user that should be added to the institute",
)
@click.option("-d", "--display-name", help="Set a new display name for a insitute")
@click.option("-l", "--loqusdb_id", help="Set a new loqusdb_id for a institute")
@click.option(
    "-r",
    "--remove-sanger",
    help="Specify email adress for a existing user that should be removed from sanger recipients",
)
@with_appcontext
def institute(
    institute_id,
    sanger_recipient,
    coverage_cutoff,
    frequency_cutoff,
    display_name,
    loqusdb_id,
    remove_sanger,
):
    """
    Update an institute
    """
    adapter = store
    LOG.info("Running scout update institute")

    try:
        adapter.update_institute(
            internal_id=institute_id,
            sanger_recipient=sanger_recipient,
            coverage_cutoff=coverage_cutoff,
            frequency_cutoff=frequency_cutoff,
            display_name=display_name,
            loqusdb_id=loqusdb_id,
            remove_sanger=remove_sanger,
        )
    except Exception as err:
        LOG.warning(err)
        raise click.Abort()
