import logging
import click

LOG = logging.getLogger(__name__)


@click.command('index', short_help='Display all indexes')
@click.option('-n', '--collection-name')
@click.pass_context
def index(context, collection_name):
    """Show all indexes in the database"""
    LOG.info("Running scout view index")
    adapter = context.obj['adapter']

    i = 0
    for index in adapter.indexes(collection_name):
        click.echo(index)
        i += 1

    if i == 0:
        LOG.info("No indexes found")



