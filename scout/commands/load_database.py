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

logger = logging.getLogger(__name__)


@click.command()
@click.option('-v', '--vcf', type=click.Path(exists=True),
              help='path to clinical VCF file to be loaded')
@click.option('-sv', '--vcf-sv', type=click.Path(exists=True),
              help='path to clinical SV VCF file to be loaded')
@click.option('-o', '--owner', help='parent institute for the case')
@click.argument('-c', '--config', type=click.File('r'), required=False)
@click.pass_context
def add(context, vcf, vcf_sv, owner, config):
    """Add a new case to Scout."""
    config_data = yaml.load(config) if config else {}
    config_data['vcf'] = vcf if vcf else config_data.get('vcf')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['owner'] = owner if owner else config_data.get('owner')

    if 'vcf' not in config_data:
        logger.warn("Please provide a vcf file (use '--vcf')")
        context.abort()
    elif 'owner' not in config_data:
        logger.warn("Please provide an owner for the case (use '--owner')")
        context.abort()

    load_scout(context.obj['adapter'], config)
