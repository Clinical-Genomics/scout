import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("collections", short_help="Display all collections")
@with_appcontext
def collections():
    """Show all collections in the database"""
    LOG.info("Running scout view collections")

    adapter = store

    for collection_name in adapter.collections():
        click.echo(collection_name)
