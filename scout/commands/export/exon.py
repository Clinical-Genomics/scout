import logging

import click

from flask.cli import with_appcontext

from scout.commands.utils import builds_option
from scout.export.exon import export_exons
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("exons", short_help="Export exons")
@builds_option
@with_appcontext
def exons(build):
    """Export all exons to chanjo compatible .bed like format"""
    LOG.info("Running scout export exons")
    adapter = store

    header = ["#Chrom\tStart\tEnd\tExonId\tTranscripts\tHgncIDs\tHgncSymbols"]

    for line in header:
        click.echo(line)

    for exon_line in export_exons(adapter, build):
        click.echo(exon_line)
