import logging

from pprint import pprint as pp

import click

from pymongo import (ASCENDING, DESCENDING, IndexModel)

log = logging.getLogger(__name__)

@click.command('index', short_help='Index the database')
@click.pass_context
def index(context):
    """Create indexes for the database"""
    log.info("Running scout index")
    adapter = context.obj['adapter']
    
    adapter.load_indexes()
