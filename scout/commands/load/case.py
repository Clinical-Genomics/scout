# -*- coding: utf-8 -*-
import datetime
import logging

from pprint import pprint as pp

import click
import yaml

from scout.load import load_scout
from scout.parse.case import parse_ped
from scout.parse.case import parse_case
from scout.build.case import build_case
from scout.exceptions import IntegrityError, ConfigError

log = logging.getLogger(__name__)

@click.command('case', short_help='Load a case')
@click.option('--vcf', type=click.Path(exists=True),
              help='path to clinical VCF file to be loaded')
@click.option('--vcf-sv', type=click.Path(exists=True),
              help='path to clinical SV VCF file to be loaded')
@click.option('--vcf-cancer', type=click.Path(exists=True),
              help='path to clinical cancer VCF file to be loaded')
@click.option('--owner', help='parent institute for the case', default='test')
@click.option('--ped', type=click.Path(exists=True))
@click.option('-u', '--update', is_flag=True)
@click.option('--no-variants', is_flag=False)
@click.argument('config', type=click.File('r'), required=False)
@click.pass_context
def case(context, vcf, vcf_sv, vcf_cancer, owner, ped, update, config, no_variants):
    """Load a case into the database.
    
    A case can be loaded without specifying vcf files and/or bam files
    """
    if config is None and ped is None:
        click.echo("You have to provide either config or ped file")
        context.abort()
    
    # Scout needs a config object with the neccessary information
    # If no config is used create a dictionary
    config_data = yaml.load(config) if config else {}

    # Default the analysis date to now if not specified in load config
    if not config_data:
        config_data['analysis_date'] = datetime.datetime.now()

    if ped:
        with open(ped, 'r') as f:
            family_id, samples = parse_ped(f)
            config_data['family'] = family_id
            config_data['samples'] = samples
    
    if 'gene_panels' in config_data:
        log.debug("handle whitespace in gene panel names")
        config_data['gene_panels'] = [panel.strip() for panel in
                                      config_data['gene_panels']]
        config_data['default_gene_panels'] = [panel.strip() for panel in
                                              config_data['default_gene_panels']]

    log.info("Use family %s" % config_data['family'])
    
    adapter = context.obj['adapter']

    if 'owner' not in config_data:
        if not owner:
            click.echo("You have to specify the owner of the case")
            context.abort()
        else:
            config_data['owner'] = owner

    config_data['vcf_snv'] = vcf if vcf else config_data.get('vcf_snv')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['vcf_cancer'] = vcf_cancer if vcf_cancer else config_data.get('vcf_cancer')
    config_data['owner'] = config_data.get('owner')
    config_data['rank_score_threshold'] = config_data.get('rank_score_threshold', 5)

    # Check that the owner exists in the database
    existing_institute = adapter.institute(config_data['owner'])
    if not existing_institute:
        log.warning("Institute %s does not exist in database", config_data['owner'])
        log.info("Please load institute with 'scout load institute --help'")
        context.abort()

    parsed_case = parse_case(config=config_data)
    
    try:
        case_obj = build_case(parsed_case, adapter)
        adapter.load_case(case_obj, update)
    except Exception as err:
        log.warning(err)
        context.abort()

    try:
        if case_obj['vcf_files'].get('vcf_snv'):
            variant_type = 'clinical'
            if update:
                adapter.delete_variants(case_id=case_obj['_id'], variant_type=variant_type)
            adapter.load_variants(
                case_obj=case_obj, 
                variant_type=variant_type, 
                category='snv',
                rank_threshold=case_obj.get('rank_score_threshold',0)
            )
    except (IntegrityError, ValueError, ConfigError, KeyError) as error:
        log.exception(error)
        context.abort()
    
    try:
        if case_obj['vcf_files'].get('vcf_sv'):
            variant_type = 'clinical'
            if update:
                adapter.delete_variants(case_id=case_obj['_id'], variant_type=variant_type)
            adapter.load_variants(
                case_obj=case_obj, 
                variant_type='clinical', 
                category='sv',
                rank_threshold=case_obj.get('rank_score_threshold',0)
            )
    except (IntegrityError, ValueError, ConfigError, KeyError) as error:
        log.exception(error)
        context.abort()

    try:
        if case_obj['vcf_files'].get('vcf_cancer'):
            variant_type = 'clinical'
            if update:
                adapter.delete_variants(case_id=case_obj['_id'], variant_type=variant_type)
            adapter.load_variants(
                case_obj=case_obj, 
                variant_type='clinical', 
                category='cancer',
                rank_threshold=case_obj.get('rank_score_threshold',0)
            )
    except (IntegrityError, ValueError, ConfigError, KeyError) as error:
        log.exception(error)
        context.abort()
