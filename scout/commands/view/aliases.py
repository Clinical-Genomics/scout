import logging
import click

from flask.cli import with_appcontext
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("aliases", short_help="Display genes by aliases")
@click.option("-b", "--build", default="37", type=click.Choice(["37", "38"]))
@click.option("-s", "--symbol", help="hgnc symbol")
@with_appcontext
def aliases(build, symbol):
    """Show all alias symbols and how they map to ids"""
    LOG.info("Running scout view aliases")
    adapter = store

    if symbol:
        alias_genes = {}
        res = adapter.gene_by_alias(symbol, build=build)
        for gene_obj in res:
            hgnc_id = gene_obj["hgnc_id"]
            # Collect the true symbol given by hgnc
            hgnc_symbol = gene_obj["hgnc_symbol"]
            # Loop aver all aliases
            for alias in gene_obj["aliases"]:
                true_id = None
                # If the alias is the same as hgnc symbol we know the true id
                if alias == hgnc_symbol:
                    true_id = hgnc_id
                # If the alias is already in the list we add the id
                if alias in alias_genes:
                    alias_genes[alias]["ids"].add(hgnc_id)
                    if true_id:
                        alias_genes[alias]["true"] = hgnc_id
                else:
                    alias_genes[alias] = {"true": hgnc_id, "ids": set([hgnc_id])}

    else:
        alias_genes = adapter.genes_by_alias(build=build)

    if len(alias_genes) == 0:
        LOG.info("No gene found for build %s", build)
        return

    click.echo("#hgnc_symbol\ttrue_id\thgnc_ids")
    for alias_symbol in alias_genes:
        info = alias_genes[alias_symbol]
        # pp(info)
        click.echo(
            "{0}\t{1}\t{2}\t".format(
                alias_symbol,
                (alias_genes[alias_symbol]["true"] or "None"),
                ", ".join([str(gene_id) for gene_id in alias_genes[alias_symbol]["ids"]]),
            )
        )
