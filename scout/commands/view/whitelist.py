import logging
import click

LOG = logging.getLogger(__name__)


@click.command('whitelist', short_help='Display whitelist')
@click.pass_context
def whitelist(context):
    """Show all objects in the whitelist collection"""
    LOG.info("Running scout view users")
    adapter = context.obj['adapter']

    ## TODO add a User interface to the adapter
    for whitelist_obj in adapter.whitelist_collection.find():
        click.echo(whitelist_obj['_id'])

