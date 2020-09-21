import logging

import click
from bson.json_util import dumps
from flask.cli import with_appcontext

from scout.commands.utils import builds_option
from scout.export.exon import export_exons
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("exons", short_help="Export exons")
@click.option("-b", "--build", default="37", type=click.Choice(["37", "38"]))
@click.option("-g", "--hgnc-id", type=int)
@click.option("--json", is_flag=True)
@with_appcontext
def exons(build, hgnc_id, json):
    """Export exons to chanjo compatible .bed like format or to json"""
    LOG.info("Running scout export exons")

    if json:  # export query results to json format
        query = {"build": build}
        if hgnc_id:
            query["hgnc_id"] = hgnc_id
        result = store.exon_collection.find(query)
        click.echo(dumps(result))
        return

    # Else return them in a human-readable table
    header = ["#Chrom\tStart\tEnd\tExonId\tTranscripts\tHgncIDs\tHgncSymbols"]

    for line in header:
        click.echo(line)

    for exon_line in export_exons(adapter, build):
        click.echo(exon_line)
