import click
import logging

from bson.json_util import dumps

from scout.export.variant import export_variants
from .utils import json_option

from scout.constants.variants_export import VCF_HEADER

LOG = logging.getLogger(__name__)

@click.command('variants', short_help='Export variants')
@click.option('-c', '--collaborator',
        help="Specify what collaborator to export variants from. Defaults to cust000",
)
@click.option('-d', '--document-id',
        help="Search for a specific variant",
)
@click.option('--case-id',
        help="Find causative variants for case",
)
@json_option
@click.pass_context
def variants(context, collaborator, document_id, case_id, json):
    """Export causatives for a collaborator in .vcf format"""
    LOG.info("Running scout export variants")
    adapter = context.obj['adapter']
    collaborator = collaborator or 'cust000'

    variants = export_variants(
        adapter,
        collaborator,
        document_id=document_id,
        case_id=case_id
    )

    if json:
        click.echo(dumps([var for var in variants]))
        return

    vcf_header = VCF_HEADER

    #If case_id is given, print more complete vcf entries, with INFO,
    #and genotypes
    if case_id:
        vcf_header[-1] = vcf_header[-1] + "\tFORMAT"
        case_obj = adapter.case(case_id=case_id)
        for individual in case_obj['individuals']:
            vcf_header[-1] = vcf_header[-1] + "\t" + individual['individual_id']

    #print header
    for line in vcf_header:
        click.echo(line)

    for variant_obj in variants:
        variant_string = get_vcf_entry(variant_obj, case_id=case_id)
        click.echo(variant_string)


def get_vcf_entry(variant_obj, case_id=None):
    """
        Get vcf entry from variant object

        Args:
            variant_obj(dict)
        Returns:
            variant_string(str): string representing variant in vcf format
    """
    if variant_obj['category'] == 'snv':
        var_type = 'TYPE'
    else:
        var_type = 'SVTYPE'

    info_field = ';'.join(
            [
                'END='+str(variant_obj['end']),
                var_type+'='+variant_obj['sub_category'].upper()
            ]
        )

    variant_string = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
        variant_obj['chromosome'],
        variant_obj['position'],
        variant_obj['dbsnp_id'],
        variant_obj['reference'],
        variant_obj['alternative'],
        variant_obj['quality'],
        ';'.join(variant_obj['filters']),
        info_field
    )

    if case_id:
        variant_string += "\tGT"
        for sample in variant_obj['samples']:
            variant_string += "\t" + sample['genotype_call']

    return variant_string
