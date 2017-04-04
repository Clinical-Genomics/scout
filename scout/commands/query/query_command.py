import logging

import click

log = logging.getLogger(__name__)

@click.command('hgnc', short_help='Check if a gene exist')
@click.option('--hgnc-symbol', '-s',
                help="A valid hgnc symbol",
)
@click.option('--hgnc-id', '-i',
                type=int,
                help="A valid hgnc id",
)
@click.option('--build', '-b',
                type=click.Choice(['37', '38']),
                default='37',
                help="Specify the genome build",
)
@click.pass_context
def hgnc(ctx, hgnc_symbol, hgnc_id, build):
    """
    Query the hgnc aliases
    """
    adapter = ctx.obj['adapter']
    
    if not (hgnc_symbol or hgnc_id):
        log.warning("Please provide a hgnc symbol or hgnc id")
        ctx.abort()

    if hgnc_id:
        result = adapter.hgnc_gene(hgnc_id, build=build)
        if result:
            hgnc_symbol = result['hgnc_symbol']
        else:
            log.warning("Gene with id %s could not be found", hgnc_id)
            ctx.abort()
    
    result = adapter.hgnc_genes(hgnc_symbol, build=build)
    
    if result.count() == 0:
        log.info("No results found")
    
    else:
        click.echo("#hgnc_id\thgnc_symbol\taliases\ttranscripts")
        for gene in result:
            click.echo("{0}\t{1}\t{2}\t{3}".format(
                gene['hgnc_id'],
                gene['hgnc_symbol'],
                ', '.join(gene['aliases']),
                ', '.join(tx['ensembl_transcript_id'] for tx in gene['transcripts']),
            ))

@click.group()
@click.pass_context
def query(context):
    """
    View objects from the database.
    """
    pass

query.add_command(hgnc)
