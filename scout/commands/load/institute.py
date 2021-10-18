import logging

import click
from flask.cli import with_appcontext

from scout.load import load_institute
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("institute", short_help="Load a institute")
@click.option("-i", "--internal-id", required=True)
@click.option("-d", "--display-name")
@click.option("-s", "--sanger-recipients", multiple=True)
@click.option("-l", "--loqusdb-id")
@with_appcontext
def institute(internal_id, display_name, sanger_recipients, loqusdb_id):
    """
    Create a new institute and add it to the database

    """
    adapter = store

    if not display_name:
        display_name = internal_id

    if sanger_recipients:
        sanger_recipients = list(sanger_recipients)

    try:
        load_institute(
            adapter=adapter,
            internal_id=internal_id,
            display_name=display_name,
            sanger_recipients=sanger_recipients,
            loqusdb_id=loqusdb_id,
        )
    except Exception as e:
        LOG.warning(e)
        raise click.Abort()
