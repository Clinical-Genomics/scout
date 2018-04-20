import logging
import click

LOG = logging.getLogger(__name__)


@click.command('genes', short_help='Display genes')
@click.option('-b', '--build', default='37', type=click.Choice(['37', '38']))
@click.pass_context
def genes(context, build):
    """Show all genes in the database"""
    LOG.info("Running scout view genes")
    adapter = context.obj['adapter']

    click.echo("Chromosom\tstart\tend\thgnc_id\thgnc_symbol")
    for gene_obj in adapter.all_genes(build=build):
        click.echo("{0}\t{1}\t{2}\t{3}\t{4}".format(
            gene_obj['chromosome'],
            gene_obj['start'],
            gene_obj['end'],
            gene_obj['hgnc_id'],
            gene_obj['hgnc_symbol'],
        ))
