import logging

import click

log = logging.getLogger(__name__)

@click.command('genes', short_help='Check if a gene exist')
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
def genes(ctx, hgnc_symbol, hgnc_id, build):
    """
    Search for genes.
    """
    adapter = ctx.obj['adapter']
    
    if hgnc_id:
        result = adapter.hgnc_gene(hgnc_id, build=build)
        if result:
            result = [result]
        else:
            log.warning("Gene with id %s could not be found", hgnc_id)
            return
    elif hgnc_symbol:
        result = [gene_obj for gene_obj in adapter.hgnc_genes(hgnc_symbol, build=build)]
    
    else:
        result = [gene_obj for gene_obj in adapter.all_genes(build=build)]
        
    
    if len(result) == 0:
        log.info("No results found")
    
    else:
        click.echo("#hgnc_id\thgnc_symbol\taliases\ttranscripts")
        for gene in result:
            hgnc_id = gene['hgnc_id']
            transcripts = adapter.transcripts(hgnc_id = hgnc_id)
            click.echo("{0}\t{1}\t{2}\t{3}".format(
                hgnc_id,
                gene['hgnc_symbol'],
                ','.join(gene['aliases']),
                ','.join(tx['ensembl_transcript_id'] for tx in transcripts),
            ))

