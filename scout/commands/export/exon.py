import logging

import click
from bson.json_util import dumps
from flask.cli import with_appcontext

from scout.commands.utils import builds_option
from scout.export.exon import export_exons, export_gene_exons
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("exons", short_help="Export exons")
@click.option("-b", "--build", default="37", type=click.Choice(["37", "38"]))
@click.option("-hgnc", "--hgnc-id", help="Limit search to exons of a gene", type=int)
@click.option("--json", help="Export to json format", is_flag=True)
@with_appcontext
def exons(build, hgnc_id, json):
    """Export exons to chanjo compatible .bed like format or to json"""
    LOG.info("Running scout export exons")

    if json:  # export query results to json format
        query = {"build": build}
        if hgnc_id:  # add hgnc ID to the exon query if hgnc ID is provided
            query["hgnc_id"] = hgnc_id
        result = store.exon_collection.find(query)
        click.echo(dumps(result))
        return

    # Else return them in a human-readable text table
    header = ["#Chrom\tStart\tEnd\tExonId\tTranscripts\tHgncIDs\tHgncSymbols"]

    for line in header:
        click.echo(line)

    if hgnc_id:  # print the exons of a single gene
        for exon_line in export_gene_exons(store, hgnc_id, build):
            click.echo(exon_line)
        return
    # Otherwise print all exons
    for exon_line in export_exons(store, build):
        click.echo(exon_line)
