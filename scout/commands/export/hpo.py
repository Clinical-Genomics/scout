import logging

import click

LOG = logging.getLogger(__name__)

@click.command('hpo_genes', short_help='Export hpo gene list')
@click.argument('hpo_term',nargs=-1)
@click.pass_context
def hpo_genes(context, hpo_term):
    """Export a list of genes based on hpo terms"""
    LOG.info("Running scout export hpo_genes")
    adapter = context.obj['adapter']
    
    header = ["#Gene_id\tCount"]

    if not hpo_term:
        LOG.warning("Please use at least one hpo term")
        context.abort()

    for line in header:
        click.echo(line)

    for term in adapter.generate_hpo_gene_list(*hpo_term):
        click.echo("{0}\t{1}".format(term[0], term[1]))
