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

logger = logging.getLogger(__name__)


@click.command()
@click.option('-f', '--vcf_file',
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-vt', '--variant_type',
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
@click.option('-o', '--owner',
                nargs=1,
                help="Specify the owner of the case."
)
@click.option('--rank_score_threshold',
                default=0,
                help="Specify the lowest rank score that should be used."
)
@click.option('--variant_number_threshold',
                default=5000,
                help="Specify the the maximum number of variants to load."
)
@click.pass_context
def load(ctx, vcf_file, variant_type, ped_file, family_type, scout_config_file,
              madeline, coverage_report, owner, rank_score_threshold,
              variant_number_threshold, analysis_type):
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
        logger.warn("Please provide a vcf file. (Use flag '-vcf/--vcf_file')")
        logger.info("Exiting")
        ctx.abort()
    logger.info("Using vcf {0}".format(scout_configs.get('load_vcf')))

    if ped_file:
        scout_configs['ped'] = ped_file
    if not scout_configs.get('ped', None):
        logger.warn("Please provide a ped file. (Use flag '-ped/--ped_file')")
        logger.info("Exiting")
        ctx.abort()
    logger.info("Using ped file {0}".format(ped_file))

    if family_type:
        scout_configs['family_type'] = family_type
    logger.info("Set family type to {0}".format(scout_configs['family_type']))

    if owner:
        scout_configs['owner'] = owner
    if not scout_configs.get('owner', None):
        logger.warn("A case has to have a owner!")
        logger.info("Exiting")
        ctx.abort()

    logger.info("Using command line specified owner {0}".format(owner))

    if analysis_type:
        scout_configs['analysis_type'] = analysis_type

    if variant_type:
        scout_configs['variant_type'] = variant_type

    if madeline:
        scout_configs['madeline'] = madeline
        logger.info("Using madeline file {0}".format(
                        scout_configs.get('madeline')))

    if coverage_report:
        scout_configs['coverage_report'] = coverage_report

    adapter = ctx.obj['adapter']
    case = adapter.add_case(
        case_lines=open(scout_configs['ped'], 'r'),
        case_type=scout_configs['family_type'],
        owner=scout_configs['owner'],
        scout_configs=scout_configs
    )

    logger.info("Delete the variants for case {0}".format(case.case_id))
    adapter.delete_variants(
        case_id=case.case_id,
        variant_type=scout_configs.get('variant_type', 'clinical')
    )
    logger.info("Load the variants for case {0}".format(case.case_id))
    adapter.add_variants(
        vcf_file=scout_configs['load_vcf'],
        variant_type=scout_configs.get('variant_type', 'clinical'),
        case=case,
        variant_number_treshold=variant_number_threshold,
        rank_score_threshold=rank_score_threshold
    )
