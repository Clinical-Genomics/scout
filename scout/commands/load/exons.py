import logging

from datetime import datetime
from pprint import pprint as pp

import click

from scout.load import (load_exons)

from scout.utils.handle import get_file_handle
from scout.utils.requests import (fetch_ensembl_exons)

LOG = logging.getLogger(__name__)

@click.command('exons', short_help='Load exons')
# @click.argument('infile', type=click.Path(exists=True))
@click.option('-b', '--build', 
    type=click.Choice(['37', '38']),
    default='37',
    show_default=True,
)
@click.pass_context
def exons(context, build):
    """Load exons into the scout database"""
    
    adapter = context.obj['adapter']
    
    start = datetime.now()
    # Test if there are any exons loaded
    
    nr_exons = adapter.exons(build=build).count()
    if nr_exons:
        LOG.warning("Dropping all exons ")
        adapter.drop_exons(build=build)
        LOG.info("Exons dropped")
    
    # Load the exons
    ensembl_exons = fetch_ensembl_exons(build=build)
    load_exons(adapter, ensembl_exons, build)

    adapter.update_indexes()
    
    LOG.info("Time to load exons: {0}".format(datetime.now() - start))

