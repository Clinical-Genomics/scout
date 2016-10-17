#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
from codecs import open
import logging

import click
from configobj import ConfigObj

from scout.load import (load_scout)

logger = logging.getLogger(__name__)


@click.command()
@click.option('-f', '--vcf_file',
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('--sv_file',
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('--variant_type',
                type=click.Choice(['clinical', 'research']),
                help="Specify the type of the variants that is being loaded."\
                        "Default='clinical'"
)
@click.option('-ped', '--ped_file',
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
@click.option('-t', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='cmms',
                help="Specify the file format of the ped (or ped like) file."
)
@click.option('-a', '--analysis_type',
                type=click.Choice(['wgs', 'wes', 'unknown']),
                help="Specify the analysis type. Default='wgs"
)
@click.option('-s', '--scout_config_file',
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
@click.option('--owner',
                help="Specify the owner of the case."
)
@click.option('-u', '--update',
                is_flag=True,
                help="Update case if it already exists."
)
@click.option('--rank_score_threshold',
                default=0,
                help="Specify the lowest rank score that should be used."
)
@click.pass_context
def load(ctx, vcf_file, sv_file, variant_type, ped_file, family_type, scout_config_file,
         madeline, coverage_report, owner, update, rank_score_threshold, analysis_type):
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
        logger.info("Use vcf specified on command line: %s" % vcf_file)
        scout_configs['load_vcf'] = vcf_file
        scout_configs['igv_vcf'] = vcf_file

    if sv_file:
        logger.info("Use sv vcf specified on command line: %s" % sv_file)
        scout_configs['sv_file'] = sv_file

    if not (scout_configs.get('load_vcf') or scout_configs.get('sv_vcf')):
        logger.warn("Please provide a vcf file. (Use flag '-vcf/--vcf_file')")
        logger.info("Exiting")
        ctx.abort()
    
    logger.info("Using vcf {0}".format(scout_configs.get('load_vcf')))

    if ped_file:
        logger.info("Use ped file specified on command line: %s" % ped_file)
        scout_configs['ped'] = ped_file
    
    if not scout_configs.get('ped'):
        logger.warn("Please provide a ped file. (Use flag '-ped/--ped_file')")
        logger.info("Exiting")
        ctx.abort()

    logger.info("Using ped file {0}".format(scout_configs['ped']))

    if family_type:
        scout_configs['family_type'] = family_type
    
    logger.info("Set family type to {0}".format(scout_configs['family_type']))

    if owner:
        logger.info("Using command line specified owner {0}".format(owner))
        scout_configs['owner'] = owner
    
    if not scout_configs.get('owner', None):
        logger.warn("A case has to have a owner!")
        logger.info("Exiting")
        ctx.abort()

    logger.info("Using owner {0}".format(scout_configs['owner']))

    if analysis_type:
        scout_configs['analysis_type'] = analysis_type

    logger.info("Using analysis type {0}".format(scout_configs['analysis_type']))

    if variant_type:
        scout_configs['variant_type'] = variant_type

    logger.info("Using variant type {0}".format(scout_configs['variant_type']))

    if madeline:
        scout_configs['madeline'] = madeline
    
    logger.info("Using madeline file {0}".format(
                        scout_configs.get('madeline')))

    adapter = ctx.obj['adapter']
    
    # try:
    load_scout(
        adapter=adapter, 
        case_file=scout_configs['ped'], 
        snv_file=scout_configs['load_vcf'], 
        owner=scout_configs['owner'], 
        sv_file=scout_configs.get('sv_file'), 
        case_type=scout_configs['family_type'], 
        variant_type=scout_configs['variant_type'], 
        update=update,
        scout_configs=scout_configs
    )
    # except Exception as e:
    #     logger.warning(e.message)
    #     ctx.abort()

