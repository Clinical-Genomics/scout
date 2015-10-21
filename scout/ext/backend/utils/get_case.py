#!/usr/bin/env python
# encoding: utf-8
"""
get_case.py

Load script for the mongo db.
Should take a directory as input, like the load part of vcf.py, and populate the mongo database.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, print_function,)

import sys
import os

import io
import json
import click
import logging
from path import path

from ..config_parser import ConfigParser
from scout.models import (Case, Individual, Institute, GeneList)

from vcf_parser import VCFParser
from ped_parser import FamilyParser

from pprint import pprint as pp

logger = logging.getLogger(__name__)


def get_institute(institute_name):
    """Take a institute name and return a institute object.

          Args:
              institute_name: A string that represents the name of an institute

          Returns:
              A mongoengine Institute object described in 
              scout.models.institute.py
    """
    return Institute(internal_id=institute_name, display_name=institute_name)

def get_individual(case, ind_id, scout_config):
    """Take a case and a individual id and return a mongo individual
    
        Args:
            case (Family): a ped_parser Family object
            ind_id (str): A individual id
            scout_configs : A ConfigObj object
        
        mongo_individual (Individual): A mongo individual
    """
    individual = case.individuals[ind_id]
    # Get info from configs for the individual
    config_info = scout_config.get(
                                'individuals', {}
                                ).get(
                                ind_id, {}
                                )
    mongo_individual = Individual()
    mongo_individual['individual_id'] = ind_id
    mongo_individual['father'] = individual.father
    mongo_individual['mother'] = individual.mother
    mongo_individual['display_name'] = individual.extra_info.get('display_name', ind_id)
    mongo_individual['sex'] = str(individual.sex)
    mongo_individual['phenotype'] = individual.phenotype
    # Path to the bam file for IGV:
    mongo_individual['bam_file'] = config_info.get('bam_path', '')

    mongo_individual['capture_kits'] = config_info.get('capture_kit', [])

    return mongo_individual
    

def get_mongo_case(case, scout_config):
    """Create a mongoengine case
    
        Args:
            case (Family): a ped_parser Family object
            scout_configs : A ConfigObj object
        
        Returns:
            mongo_case (Case): A mongo case
    """
    # Check if there is a owner of the case
    try:
        owner = scout_config['owner']
    except KeyError as e:
        logger.error("Scout config must include a owner")
        raise e
    
    case_id = case.family_id
    # Check if there are any collaborators for the case, a case can belong to
    # several institutes
    collaborators = scout_config.get('collaborators', set())
    if collaborators:
        if type(collaborators) == type(list()):
            collaborators = set(collaborators)
        else:
            collaborators = set([collaborators])
    
    collaborators.add(owner)

    logger.info("Collaborators found: {0}".format(','.join(collaborators)))

    # Create a mongoengine case
    mongo_case_id = '_'.join([owner, case_id])
    
    mongo_case = Case(case_id=mongo_case_id)
    logger.debug("Setting case id to: {0}".format(mongo_case_id))
    
    mongo_case['owner'] = owner
    logger.debug("Setting owner to: {0}".format(owner))
    
    mongo_case['collaborators'] = list(collaborators)
    logger.debug("Setting collaborators to: {0}".format(
      ', '.join(collaborators)))
    
    # We use the family id as display name for scout
    mongo_case['display_name'] = case_id
    logger.debug("Setting display name to: {0}".format(case_id))
    
    # Get the path of vcf from configs
    mongo_case['vcf_file'] = scout_config.get('igv_vcf', '')
    logger.debug("Setting igv vcf file to: {0}".format(
      scout_config.get('igv_vcf', '')))
    
    # Add the genome build information
    mongo_case['genome_build'] = scout_config.get('human_genome_build', '')
    logger.debug("Setting genome build to: {0}".format(
      scout_config.get('human_genome_build', '')))
    
    # Get the genome version
    mongo_case['genome_version'] = float(scout_config.get('human_genome_version', '0'))
    logger.debug("Setting genome version to: {0}".format(
      scout_config.get('human_genome_version', '0')))
    
    # Check the analysis date
    mongo_case['analysis_date'] = scout_config.get('analysis_date', '')
    logger.debug("Setting analysis date to: {0}".format(
      scout_config.get('analysis_date', '')))
    
    # Add the pedigree picture, this is a xml file that will be read and 
    # saved in the mongo database
    madeline_path = path(scout_config.get('madeline', '/__menoexist.tXt'))
    
    if madeline_path.exists():
        logger.debug("Found madeline info")
        with madeline_path.open('r') as handle:
            mongo_case['madeline_info'] = handle.read()
            logger.debug("Madeline file was read succesfully")
    else:
        logger.info("No madeline file found. Skipping madeline file.")
    
    # Add the coverage report
    coverage_report_path = path(scout_config.get('coverage_report', '/__menoexist.tXt'))
    if coverage_report_path.exists():
        logger.debug("Found a coverage report")
        with coverage_report_path.open('rb') as handle:
            mongo_case['coverage_report'] = handle.read()
            logger.debug("Coverage was read succesfully")
    else:
        logger.info("No coverage report found. Skipping coverage report.")
    
    clinical_gene_lists = []
    research_gene_lists = []
    
    for gene_list in scout_config.get('gene_lists', {}):
        logger.info("Found gene list {0}".format(gene_list))
        list_info = scout_config['gene_lists'][gene_list]

        list_type = list_info.get('type', 'clinical')
        list_id = list_info.get('name', '')
        version = float(list_info.get('version', 0))
        date = list_info.get('date', '')
        display_name = list_info.get('full_name', list_id)
        
        list_object = GeneList(
            list_id=list_id,
            version=version,
            date=date,
            display_name=display_name
        )
        
        if list_type == 'clinical':
            logger.info("Adding {0} to clinical gene lists".format(list_object))
            clinical_gene_lists.append(list_object)
        else:
            logger.info("Adding {0} to research gene lists".format(list_object))
            research_gene_lists.append(list_object)
        
        mongo_case['clinical_gene_lists'] = clinical_gene_lists
        mongo_case['research_gene_lists'] = research_gene_lists
        
        default_gene_lists = scout_config.get('default_gene_lists', [])
        
        mongo_case['default_gene_lists'] = list(default_gene_lists)
    
    return mongo_case
    
def get_case(scout_configs, family_type):
    """
    Take a case file and return the case on the specified format.
    
    Only one case per pedigree file is allowed.
    
    Args:
      family_type : A string that describe the format of the ped file
      scout_configs (dict): A dictionary scout info.
    
    Returns:
      case : A mongo engine object that describe the case
              found in the pedigree file.
    
    """
    # Use ped_parser to get information from the pedigree file
    case_parser = FamilyParser(open(scout_configs['ped'], 'r'), 
                               family_type=family_type)
    
    if len(case_parser.families) != 1:
        raise SyntaxError("Only one case per ped file is allowed")
    
    case_id = list(case_parser.families.keys())[0]
    case = case_parser.families[case_id]

    mongo_case = get_mongo_case(
        case=case, 
        scout_config=scout_configs
    )

    individuals = []
    affected_individuals = case.affected_individuals
    
    for ind_id in affected_individuals:
        individuals.append(get_individual(
            case=case, 
            ind_id=ind_id, 
            scout_config=scout_configs
        ))

    for ind_id in case.individuals:
        if ind_id not in affected_individuals:
            individuals.append(get_individual(
                case=case, 
                ind_id=ind_id, 
                scout_config=scout_configs
            ))
    
    mongo_case['individuals'] = individuals

    return mongo_case


@click.command()
@click.option('-p', '--ped_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
@click.option('-c', '--scout_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the config file for loading the variants."
)
@click.option('-m', '--madeline',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the madeline file with the pedigree."
)
@click.option('-t', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='cmms',
                nargs=1,
                help="Specify the file format of the ped (or ped like) file."
)
@click.option('-i', '--institute',
                default='CMMS',
                nargs=1,
                help="Specify the institute that the file belongs to."
)
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(ped_file, scout_config_file, family_type, madeline, institute, verbose):
    """
    Test get_case and get_institute.
    """

    setup_configs = {}

    if scout_config_file:
        setup_configs = ConfigParser(scout_config_file)
      
    if ped_file:
        setup_configs['ped'] = ped_file
      
    if madeline:
        setup_configs['madeline'] = madeline
      
    if institute:
        setup_configs['institutes'] = [institute]
      
    # Check that the ped file is provided:
    if not setup_configs.get('ped', None):
        print("Please provide a ped file.(Use flag '-p/--ped_file')", file=sys.stderr)
        sys.exit(0)

    mongo_case = get_case(setup_configs, family_type)
    # print(mongo_case.to_json())

if __name__ == '__main__':
    cli()
