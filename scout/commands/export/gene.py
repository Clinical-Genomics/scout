import logging

import click

from scout.constants import BUILDS

from scout.export.gene import export_genes

LOG = logging.getLogger(__name__)

@click.command('genes', short_help='Export genes')
@click.option('-b', '--build',
    default='37',
    show_default=True,
    type=click.Choice(BUILDS),
)
@click.pass_context
def genes(context, build):
    """Export all genes to .bed like format"""
    LOG.info("Running scout export genes")
    adapter = context.obj['adapter']
    
    header = ["#Chrom\tStart\tEnd\tHgncSymbol\tHgncID"]

    for line in header:
        click.echo(line)

    gene_string = ("{0}\t{1}\t{2}\t{3}\t{4}")

    for gene in export_genes(adapter):
        click.echo(gene_string.format(
            gene['chromosome'],
            gene['start'],
            gene['end'],
            gene['hgnc_symbol'],
            gene['hgnc_id']
        ))
