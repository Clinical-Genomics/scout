import logging
from flask.cli import with_appcontext, current_app
from scout.server.extensions import store
import click

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

@click.group()
def query():
    """
    View objects from the database.
    """
    pass


@query.command('hgnc', short_help='Check if a gene exist')
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
@with_appcontext
def hgnc(hgnc_symbol, hgnc_id, build):
    """
    Query the hgnc aliases
    """

    adapter = store

    if not (hgnc_symbol or hgnc_id):
        log.warning("Please provide a hgnc symbol or hgnc id")
        raise click.Abort()

    if hgnc_id:
        result = adapter.hgnc_gene(hgnc_id, build=build)
        if result:
            hgnc_symbol = result['hgnc_symbol']
        else:
            log.warning("Gene with id %s could not be found", hgnc_id)
            raise click.Abort()

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
                ', '.join(tx['ensembl_transcript_id'] for tx in gene['transcripts']) if gene.get('transcripts') else '',
            ))

query.add_command(hgnc)
