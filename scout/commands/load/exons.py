import logging

from datetime import datetime
from pprint import pprint as pp

import click
from flask.cli import with_appcontext

from scout.load import (load_exons)

from scout.utils.handle import get_file_handle
from scout.utils.requests import (fetch_ensembl_exons)
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

@click.command('exons', short_help='Load exons')
# @click.argument('infile', type=click.Path(exists=True))
@click.option('-b', '--build',
    type=click.Choice(['37', '38']),
    default='37',
    show_default=True,
)
@with_appcontext
def exons(build):
    """Load exons into the scout database"""

    adapter = store

    start = datetime.now()
    # Test if there are any exons loaded

    existing_exon = adapter.exon(build=build)
    if existing_exon:
        LOG.warning("Dropping all exons ")
        adapter.drop_exons(build=build)
        LOG.info("Exons dropped")

    # Load the exons
    # ensembl_exons = fetch_ensembl_exons(build=build)
    ensembl_exons = []
    load_exons(adapter, ensembl_exons, build)

    adapter.update_indexes()

    LOG.info("Time to load exons: {0}".format(datetime.now() - start))
