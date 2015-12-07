#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
import sys
import os
import logging

import click

from configobj import ConfigObj

from scout.ext.backend import (load_mongo_db)

logger = logging.getLogger(__name__)

@click.command()
@click.option('-vcf', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-ped', '--ped_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
@click.option('-s', '--scout_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the scout config file."
)
@click.option('-m', '--madeline',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the madeline file with the pedigree."
)
@click.option('-r', '--coverage_report',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the coverage report file."
)
@click.option('-t', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='cmms',
                nargs=1,
                help="Specify the file format of the ped (or ped like) file."
)
@click.option('-vt', '--variant_type',
                type=click.Choice(['clinical', 'research']),
                default='clinical',
                nargs=1,
                help="Specify the type of the variants that is being loaded."
)
@click.option('-i', '--owner',
                nargs=1,
                help="Specify the owner of the case."
)
@click.option('--rank_score_threshold',
                default=0,
                nargs=1,
                help="Specify the lowest rank score that should be used."
)
@click.option('--variant_number_threshold',
                default=5000,
                nargs=1,
                help="Specify the the maximum number of variants to load."
)
@click.pass_context
def load(ctx, vcf_file, variant_type, ped_file, family_type, scout_config_file, 
              madeline, coverage_report, owner, rank_score_threshold, 
              variant_number_threshold):
    """
    Load the mongo database.
    
    Command line arguments will override what's in the config file.
    
    """
    # Check if vcf file exists and that it has the correct naming:
    scout_configs = {}
    
    logger.info("Running load_mongo")
    if scout_config_file:
        scout_configs = ConfigObj(scout_config_file)
        logger.info("Using scout config file {0}".format(scout_config_file))
    
    if vcf_file:
        scout_configs['load_vcf'] = vcf_file
        scout_configs['igv_vcf'] = vcf_file
    
    if not scout_configs.get('load_vcf'):
        logger.warning("Please provide a vcf file.(Use flag '-vcf/--vcf_file')")
        logger.info("Exiting")
        sys.exit(1)
    logger.info("Using vcf {0}".format(scout_configs.get('load_vcf')))
    
    if ped_file:
        logger.info("Using command line specified ped file {0}".format(ped_file))
        scout_configs['ped'] = ped_file
    if not scout_configs.get('ped', None):
        logger.warning("Please provide a ped file.(Use flag '-ped/--ped_file')")
        logger.info("Exiting")
        sys.exit(1)

    if owner:
        scout_configs['owner'] = owner
    if not scout_configs.get('owner', None):
        logger.warning("A case has to have a owner!")
        logger.info("Exiting")
        sys.exit(1)
    
    logger.info("Using command line specified owner {0}".format(
        institute))
    
    if madeline:
        scout_configs['madeline'] = madeline
        logger.info("Using madeline file {0}".format(
                        scout_configs.get('madeline')))
    
    if coverage_report:
        scout_configs['coverage_report'] = coverage_report
    
    adapter = ctx.parent.adapter
    
    
    # my_vcf = load_mongo_db(
    #                         scout_configs,
    #                         vcf_config_file,
    #                         family_type,
    #                         mongo_db=mongo_db,
    #                         username=username,
    #                         password=password,
    #                         variant_type=variant_type,
    #                         port=port,
    #                         host=host,
    #                         rank_score_threshold=rank_score_threshold,
    #                         variant_number_threshold=variant_number_threshold
    #                       )
