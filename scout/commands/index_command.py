import logging

import click

LOG = logging.getLogger(__name__)

@click.command('index', short_help='Index the database')
@click.option('--update', help="Update the indexes", is_flag=True)
@click.pass_context
def index(context, update):
    """Create indexes for the database"""
    LOG.info("Running scout index")
    adapter = context.obj['adapter']
    
    if update:
        adapter.update_indexes()
    else:
        adapter.load_indexes()
