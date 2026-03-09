import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("genes", short_help="Delete genes")
@click.option("-b", "build", type=click.Choice(["37", "38"]))
@with_appcontext
def genes(build):
    """Delete all genes in the database"""
    LOG.info("Running scout delete genes")
    adapter = store

    if build:
        LOG.info("Dropping genes collection for build: %s", build)
    else:
        LOG.info("Dropping all genes")
    adapter.drop_genes(build=build)


@click.command("exons", short_help="Delete exons")
@click.option("-b", "build", type=click.Choice(["37", "38"]))
@with_appcontext
def exons(build):
    """Delete all exons in the database"""
    LOG.info("Running scout delete exons")
    adapter = store

    adapter.drop_exons(build)
