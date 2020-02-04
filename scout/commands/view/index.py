import logging
import click

from flask.cli import with_appcontext
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("index", short_help="Display all indexes")
@click.option("-n", "--collection-name")
@with_appcontext
def index(collection_name):
    """Show all indexes in the database"""
    LOG.info("Running scout view index")
    adapter = store

    i = 0
    click.echo("collection\tindex")
    for collection in adapter.collections():
        for index in adapter.indexes(collection):
            if collection_name and collection != collection_name:
                continue
            click.echo("{0}\t{1}".format(collection, index))
            i += 1

    if i == 0:
        LOG.info("No indexes found")
