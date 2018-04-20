import logging

import click

LOG = logging.getLogger(__name__)


@click.command('collections', short_help='Display all collections')
@click.pass_context
def collections(context):
    """Show all collections in the database"""
    LOG.info("Running scout view collections")

    adapter = context.obj['adapter']

    for collection_name in adapter.collections():
        click.echo(collection_name)
