#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
import logging

import click
import yaml

from scout.load import load_scout
from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


@click.command()
@click.option('--vcf', 
              type=click.Path(exists=True),
              help='path to clinical VCF file to be loaded'
)
@click.option('--vcf-sv', 
              type=click.Path(exists=True),
              help='path to clinical SV VCF file to be loaded'
)
@click.option('--owner', 
              help='parent institute for the case'
)
@click.option('--ped', 
              type=click.File('r')
)
@click.option('-u', '--update', 
              is_flag=True
)
@click.argument('config', 
              type=click.File('r'), 
              required=False
)
@click.pass_context
def load(context, vcf, vcf_sv, owner, ped, update, config):
    """Add a new case to Scout."""
    if config is None and ped is None:
        click.echo("you have to provide either config or ped file")
        context.abort()

    config_data = yaml.load(config) if config else {}

    config_data['vcf_snv'] = vcf if vcf else config_data.get('vcf')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['owner'] = owner if owner else config_data.get('owner')
    config_data['rank_treshold'] = config_data.get('rank_treshold') or 5

    from pprint import pprint as pp
    pp(config_data)
    context.abort()
    
    if not (config_data.get('vcf_snv') or config_data.get('vcf_sv')):
        logger.warn("Please provide a vcf file (use '--vcf')")
        context.abort()

    if not config_data.get('owner'):
        logger.warn("Please provide an owner for the case (use '--owner')")
        context.abort()
    
    try:
        load_scout(context.obj['adapter'], config_data, ped=ped, update=update)
    except (IntegrityError, ValueError) as error:
        click.echo(error)
        context.abort()
