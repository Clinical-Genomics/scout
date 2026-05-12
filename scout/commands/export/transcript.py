import logging

import click
from flask.cli import with_appcontext

from scout.commands.utils import builds_option
from scout.export.transcript import export_transcripts
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("transcripts", short_help="Export transcripts")
@builds_option
@with_appcontext
def transcripts(build):
    """Export all transcripts to .bed like format"""
    LOG.info("Running scout export transcripts")
    adapter = store

    genome_build = "38" if (build == "GRCh38") else build

    header = ["#Chrom\tStart\tEnd\tTranscript\tRefSeq\tHgncID"]

    for line in header:
        click.echo(line)

    chr_prefix = ""
    if build == "GRCh38":
        chr_prefix = "chr"
    transcript_string = "{0}{1}\t{2}\t{3}\t{3}\t{4}\t{5}"

    for tx_obj in export_transcripts(adapter, genome_build):
        click.echo(
            f"{chr_prefix}{tx_obj["chrom"]}\t{tx_obj["start"]}\t{tx_obj["end"]}\t{tx_obj['ensembl_transcript_id']}\t{tx_obj.get('refseq_id', '')}\t{tx_obj['hgnc_id']}"
        )
