# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

import click

from scout.load import load_scout
from scout.parse.case import (parse_case_data)
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
@click.option('--peddy-ped', type=click.Path(exists=True),
              help='path to a peddy.ped file')
@click.option('--peddy-sex', type=click.Path(exists=True),
              help='path to a sex_check.csv file')
@click.option('--peddy-check', type=click.Path(exists=True),
              help='path to a ped_check.csv file')
@click.pass_context
def case(context, vcf, vcf_sv, vcf_cancer, owner, ped, update, config,
         no_variants, peddy_ped, peddy_sex, peddy_check):
    """Load a case into the database.

    A case can be loaded without specifying vcf files and/or bam files
    """
    adapter = context.obj['adapter']

    if config is None and ped is None:
        click.echo("You have to provide either config or ped file")
        context.abort()

    # Scout needs a config object with the neccessary information
    # If no config is used create a dictionary
    try:
        config_data = parse_case_data(
            config=config,
            ped=ped,
            owner=owner,
            vcf_snv=vcf,
            vcf_sv=vcf_sv,
            vcf_cancer=vcf_cancer,
            peddy_ped=peddy_ped,
            peddy_sex=peddy_sex,
            peddy_check=peddy_check
        )
    except SyntaxError as err:
        log.warning(err)
        context.abort()

    log.info("Use family %s" % config_data['family_id'])

    try:
        case_obj = adapter.load_case(config_data, update)
    except IntegrityError as err:
        log.warning(err)
        context.abort()
