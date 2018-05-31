import click
import logging

from scout.export.variant import export_causatives

LOG = logging.getLogger(__name__)

@click.command('variants', short_help='Export variants')
@click.option('-c', '--collaborator',
        help="Specify what collaborator to export variants from. Defaults to cust000",
)
@click.pass_context
def variants(context, collaborator):
    """Export causatives for a collaborator in .vcf format"""
    LOG.info("Running scout export variants")
    adapter = context.obj['adapter']
    collaborator = collaborator or 'cust000'

    header = [
        "##fileformat=VCFv4.2",
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
    ]

    for line in header:
        click.echo(line)

    for variant in export_causatives(adapter, collaborator):
        click.echo(variant)