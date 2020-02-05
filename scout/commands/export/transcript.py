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

    header = ["#Chrom\tStart\tEnd\tTranscript\tRefSeq\tHgncID"]

    for line in header:
        click.echo(line)

    transcript_string = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}"

    for tx_obj in export_transcripts(adapter, build):
        click.echo(
            transcript_string.format(
                tx_obj["chrom"],
                tx_obj["start"],
                tx_obj["end"],
                tx_obj["ensembl_transcript_id"],
                tx_obj.get("refseq_id", ""),
                tx_obj["hgnc_id"],
            )
        )
