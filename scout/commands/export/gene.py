import logging

import click

from bson.json_util import dumps

from scout.commands.utils import builds_option

from scout.export.gene import export_genes

from .utils import (build_option, json_option)

LOG = logging.getLogger(__name__)

@click.command('genes', short_help='Export genes')
@build_option
@json_option
@click.pass_context
def genes(context, build, json):
    """Export all genes from a build"""
    LOG.info("Running scout export genes")
    adapter = context.obj['adapter']

    result = adapter.all_genes(build=build)
    if json:
        click.echo(dumps(result))
        return
        
    gene_string = ("{0}\t{1}\t{2}\t{3}\t{4}")
    click.echo("#Chromosom\tStart\tEnd\tHgnc_id\tHgnc_symbol")
    for gene_obj in result:
        click.echo(gene_string.format(
            gene_obj['chromosome'],
            gene_obj['start'],
            gene_obj['end'],
            gene_obj['hgnc_id'],
            gene_obj['hgnc_symbol'],
        ))

