import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("hgnc", short_help="Check if a gene exist")
@click.option("--hgnc-symbol", "-s", help="A valid hgnc symbol")
@click.option("--hgnc-id", "-i", type=int, help="A valid hgnc id")
@click.option(
    "--build",
    "-b",
    type=click.Choice(["37", "38"]),
    default="37",
    help="Specify the genome build",
)
@with_appcontext
def hgnc(hgnc_symbol, hgnc_id, build):
    """
    Query the hgnc aliases
    """

    adapter = store

    if not (hgnc_symbol or hgnc_id):
        LOG.warning("Please provide a hgnc symbol or hgnc id")
        raise click.Abort()

    if hgnc_id:
        result = adapter.hgnc_gene_caption(hgnc_id, build=build)
        if not result:
            LOG.warning("Gene with id %s could not be found", hgnc_id)
            return
        hgnc_symbol = result["hgnc_symbol"]

    result = adapter.hgnc_genes(hgnc_symbol, build=build)

    i = 0
    click.echo("#hgnc_id\thgnc_symbol\taliases")
    for i, gene in enumerate(result, 1):
        click.echo(
            "{0}\t{1}\t{2}".format(gene["hgnc_id"], gene["hgnc_symbol"], ", ".join(gene["aliases"]))
        )

    if i == 0:
        LOG.info("No results found")
