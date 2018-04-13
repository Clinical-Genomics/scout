import logging
import click

LOG = logging.getLogger(__name__)


@click.command('aliases', short_help='Display genes by aliases')
@click.option('-b', '--build', default='37', type=click.Choice(['37', '38']))
@click.pass_context
def aliases(context, build):
    """Show all alias symbols and how they map to ids"""
    LOG.info("Running scout view aliases")
    adapter = context.obj['adapter']

    alias_genes = adapter.genes_by_alias(build=build)
    click.echo("#hgnc_symbol\ttrue_id\thgnc_ids")
    for alias_symbol in alias_genes:
        info = alias_genes[alias_symbol]
        # pp(info)
        click.echo("{0}\t{1}\t{2}\t".format(
            alias_symbol,
            (alias_genes[alias_symbol]['true'] or 'None'),
            ', '.join([str(gene_id) for gene_id in alias_genes[alias_symbol]['ids']])
        )
        )

