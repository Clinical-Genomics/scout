import logging

from datetime import datetime
from pprint import pprint as pp

import click
from flask.cli import with_appcontext

from scout.load import load_exons

from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import fetch_ensembl_exons
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("exons", short_help="Load exons")
@click.option(
    "-e",
    "--exons-file",
    type=click.Path(exists=True),
    help="Path to file with ensembl exons",
)
@click.option("-b", "--build", type=click.Choice(["37", "38"]), default="37", show_default=True)
@with_appcontext
def exons(build, exons_file):
    """Load exons into the scout database. If no file, fetch exons from ensembl biomart"""
    adapter = store
    LOG.info("Running scout load exons")
    start = datetime.now()
    # Test if there are any exons loaded

    existing_exon = adapter.exon(build=build)
    if existing_exon:
        LOG.warning("Dropping all exons ")
        adapter.drop_exons(build=build)
        LOG.info("Exons dropped")

    # Load the exons
    nr_exons = 0
    if exons_file:
        ensembl_exons = get_file_handle(exons_file)
        for nr_exons, line in enumerate(ensembl_exons, 1):
            pass
        ensembl_exons = get_file_handle(exons_file)
    else:
        ensembl_exons = fetch_ensembl_exons(build=build)
        nr_exons = 1360000

    try:
        load_exons(adapter, ensembl_exons, build, nr_exons=nr_exons)
    except Exception as err:
        LOG.warning("Something went wrong with ensembl biomart")
        # LOG.info("Try to fetch one chromosome at the time")
        LOG.info("Please download a mart dump manually, see instructions in user guide for admins")
        return

    adapter.update_indexes()

    LOG.info("Time to load exons: {0}".format(datetime.now() - start))
