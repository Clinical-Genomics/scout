import logging
import click
from pprint import pprint as pp

LOG = logging.getLogger(__name__)


@click.command('transcripts', short_help='Display transcripts')
@click.option('-b', '--build', default='37', type=click.Choice(['37', '38']))
@click.pass_context
def transcripts(context, build):
    """Show all transcripts in the database"""
    LOG.info("Running scout view transcripts")
    adapter = context.obj['adapter']

    click.echo("Chromosom\tstart\tend\ttranscript_id\thgnc_id\trefseq\tis_primary")
    for tx_obj in adapter.transcripts(build=build):
        click.echo("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(
            tx_obj['chrom'],
            tx_obj['start'],
            tx_obj['end'],
            tx_obj['ensembl_transcript_id'],
            tx_obj['hgnc_id'],
            tx_obj.get('refseq_id', ''),
            tx_obj.get('is_primary') or '',
        ))
        
