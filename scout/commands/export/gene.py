import logging

import click
from bson.json_util import dumps
from flask.cli import with_appcontext

from scout.commands.utils import builds_option
from scout.export.gene import export_genes
from scout.server.extensions import store

from .utils import (build_option, json_option)

LOG = logging.getLogger(__name__)

@click.command('genes', short_help='Export genes')
@build_option
@json_option
@click.option('-i', '--hgnc-id',
    type=int,
    help="Specify what gene to fetch"
)
@with_appcontext
def genes(build, json, hgnc_id):
    """Export genes from Scout"""
    LOG.info("Running scout export genes")
    adapter = store
    if hgnc_id:
        gene_obj = adapter.hgnc_gene(hgnc_id, build=build)
        if not gene_obj:
            LOG.info("No result found for %s", hgnc_id)
            return
        gene_list = [gene_obj]
    else:
        result = adapter.all_genes(build=build)
        gene_list = list(result)
    if '38' in build:
        for gene_obj in gene_list:
            if gene_obj['chromosome'] == 'MT':
                gene_obj['chromosome'] = 'M'
            gene_obj['chromosome'] = ''.join(['chr',gene_obj['chromosome']])

    if json:
        click.echo(dumps(gene_list))
        return


    gene_string = ("{0}\t{1}\t{2}\t{3}\t{4}")
    click.echo("#Chromosome\tStart\tEnd\tHgnc_id\tHgnc_symbol")
    for gene_obj in gene_list:
        click.echo(gene_string.format(
            gene_obj['chromosome'],
            gene_obj['start'],
            gene_obj['end'],
            gene_obj['hgnc_id'],
            gene_obj['hgnc_symbol'],
        ))
