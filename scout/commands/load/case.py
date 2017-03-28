# -*- coding: utf-8 -*-
import datetime
import logging

import click
import yaml

from scout.load import load_scout
from scout.parse.case import parse_ped
from scout.exceptions import IntegrityError, ConfigError

log = logging.getLogger(__name__)

@click.command('case', short_help='Load a case')
@click.option('--vcf', type=click.Path(exists=True),
              help='path to clinical VCF file to be loaded')
@click.option('--vcf-sv', type=click.Path(exists=True),
              help='path to clinical SV VCF file to be loaded')
@click.option('--owner', help='parent institute for the case', default='test')
@click.option('--ped', type=click.Path(exists=True))
@click.option('-u', '--update', is_flag=True)
@click.argument('config', type=click.File('r'), required=False)
@click.pass_context
def case(context, vcf, vcf_sv, owner, ped, update, config):
    """Load a case into the database"""
    if config is None and ped is None:
        click.echo("You have to provide either config or ped file")
        context.abort()

    config_data = yaml.load(config) if config else {}

    if not config_data:
        config_data['analysis_date'] = datetime.datetime.now()

    if ped:
        with open(ped, 'r') as f:
            family_id, samples = parse_ped(f)
            config_data['family'] = family_id

    if 'gene_panels' in config_data:
        log.debug("handle whitespace in gene panel names")
        config_data['gene_panels'] = [panel.strip() for panel in
                                      config_data['gene_panels']]
        config_data['default_gene_panels'] = [panel.strip() for panel in
                                              config_data['default_gene_panels']]

    log.info("Use family %s" % config_data['family'])
    # check if the analysis is from a newer analysis
    adapter = context.obj['adapter']

    if 'owner' not in config_data:
        if not owner:
            click.echo("You have to specify the owner of the case")
            context.abort()
        else:
            config_data['owner'] = owner

    existing_case = adapter.case(
                        institute_id=config_data['owner'], 
                        display_name=config_data['family']
                    )
    
    if existing_case:
        new_analysisdate = config_data.get('analysis_date')
        if new_analysisdate and new_analysisdate > existing_case['analysis_date']:
            log.info("updated analysis - updating existing case")
            # update by default!
            update = True
        else:
            log.warning("Case already exists in database")
            context.abort()
    else:
        log.info("Case does not exist in database")

    config_data['vcf_snv'] = vcf if vcf else config_data.get('vcf_snv')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['owner'] = config_data.get('owner')
    config_data['rank_score_threshold'] = config_data.get('rank_score_threshold', 5)

    if not (config_data.get('vcf_snv') or config_data.get('vcf_sv')):
        log.warn("Please provide a vcf file (use '--vcf')")
        context.abort()

    if not config_data.get('owner'):
        log.warn("Please provide an owner for the case (use '--owner')")
        context.abort()

    try:
        load_scout(adapter, config_data, ped=ped, update=update)
    except (IntegrityError, ValueError, ConfigError, KeyError) as error:
        log.exception(error)
        context.abort()
