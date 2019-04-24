import logging
import click

from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command('whitelist', short_help='Display whitelist')
@with_appcontext
def whitelist():
    """Show all objects in the whitelist collection"""
    LOG.info("Running scout view users")
    adapter = store

    ## TODO add a User interface to the adapter
    for whitelist_obj in adapter.whitelist_collection.find():
        click.echo(whitelist_obj['_id'])
