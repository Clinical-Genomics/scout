import logging
import click

from pymongo import (ASCENDING, DESCENDING)

log = logging.getLogger(__name__)

@click.command('index', short_help='Index the database')
@click.pass_context
def index(context):
    """Create indexes for the database"""
    log.info("Running scout index")
    adapter = context.obj['adapter']
    
    indexes = {
        'hgnc_collection': [
            [('build', ASCENDING), ('chromosome', ASCENDING)],
        ],
        'variant_collection': [
            [('case_id', ASCENDING),('rank_score', DESCENDING)],
            [('case_id', ASCENDING),('variant_rank', ASCENDING)]
        ]
    }
    
    log.info("Creating indexes")
    
    for collection in indexes:
        for index in indexes[collection]:
            index_name = adapter.db[collection].create_index(index)
            log.info("Creating index {0} in collection {1}".format(
                index_name, collection
            ))