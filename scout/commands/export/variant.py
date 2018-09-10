import click
import logging

from bson.json_util import dumps

from scout.export.variant import export_variants
from .utils import json_option

LOG = logging.getLogger(__name__)

@click.command('variants', short_help='Export variants')
@click.option('-c', '--collaborator',
        help="Specify what collaborator to export variants from. Defaults to cust000",
)
@click.option('-d', '--document-id',
        help="Search for a specific variant",
)
@json_option
@click.pass_context
def variants(context, collaborator, document_id, json):
    """Export causatives for a collaborator in .vcf format"""
    LOG.info("Running scout export variants")
    adapter = context.obj['adapter']
    collaborator = collaborator or 'cust000'
    
    variants = export_variants(adapter, collaborator, document_id=document_id)
    
    if json:
        click.echo(dumps([var for var in variants]))
        return
    
    vcf_header = [
        "##fileformat=VCFv4.2",
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
    ]

    for line in vcf_header:
        click.echo(line)

    #put variants in a dict to get unique ones
    variant_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}")

    for variant_obj in variants:
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