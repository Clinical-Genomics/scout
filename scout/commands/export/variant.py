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

    #put variants in a dict to get unique ones
    variant_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}")

    ##TODO add option to give output in json format
    for variant_obj in export_causatives(adapter, collaborator):
        click.echo(variant_string.format(
            variant_obj['chromosome'],
            variant_obj['position'],
            variant_obj['dbsnp_id'],
            variant_obj['reference'],
            variant_obj['alternative'],
            variant_obj['quality'],
            ';'.join(variant_obj['filters']),
            '.'
        ))