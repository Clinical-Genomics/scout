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
    
    if hgnc_id:
        result = adapter.hgnc_gene(hgnc_id, build=build)
    
    elif hgnc_symbol:
        result = adapter.hgnc_genes(hgnc_symbol)
    else:
        log.warning("Please provide a hgnc symbol or hgnc id")
        ctx.abort()
    
    if results.count() == 0:
        log.info("No results found")
    
    else:
        for result in results:
            click.echo(result)

@click.group()
@click.pass_context
def query(context):
    """
    View objects from the database.
    """
    pass

query.add_command(hgnc)
