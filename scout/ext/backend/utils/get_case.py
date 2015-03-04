#!/usr/bin/env python
# encoding: utf-8
"""
get_case.py

Load script for the mongo db.
Should take a directory as input, like the load part of vcf.py, and populate the mongo database.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, unicode_literals, print_function,)

import sys
import os

import io
import json
import click

from ..config_parser import ConfigParser
from ....models import (Case, Individual, Institute, GeneList)

from vcf_parser import VCFParser
from ped_parser import FamilyParser

from pprint import pprint as pp


def get_institute(institute_name):
  """
  Take a institute name and return a institute object.

  Args:
    institute_name: A string that represents the name of an institute

  Returns:
    A mongoengine Institute object described in scout.models.institute.py
  """
  return Institute(internal_id=institute_name, display_name=institute_name)

def get_case(scout_configs, family_type):
  """
  Take a case file and return the case on the specified format.

  Only one case per pedigree file is allowed.

  Args:
    ped_file    : The path to a ped file
    family_type : A string that describe the format of the ped file
    scout_configs (dict): A dictionary scout info.

  Returns:
    case : A mongo engine object that describe the case
            found in the pedigree file.

  """
  # Use ped_parser to get information from the pedigree file
  case_parser = FamilyParser(scout_configs['ped'], family_type=family_type)
  # A case can belong to several institutes
  institute_names = scout_configs.get('institutes', None)

  for case in case_parser.to_json():
    # Create a mongo engine case
    mongo_case = Case(case_id='_'.join(['_'.join(institute_names), case['family_id']]))
    # We use the family id as display name for scout
    mongo_case['display_name'] = case['family_id']
    # Get the path of vcf from configs
    mongo_case['vcf_file'] = scout_configs.get('igv_vcf', '')
    # Add the genome build information
    mongo_case['genome_build'] = scout_configs.get('human_genome_build', '')
    mongo_case['genome_version'] = float(scout_configs.get('human_genome_version', '0'))
    
    mongo_case['analysis_date'] = scout_configs.get('analysis_date', '') 
    
    # Add the pedigree picture
    madeline_file = scout_configs.get('madeline', None)
    if madeline_file:
      with open(madeline_file, 'r') as f:
        mongo_case['madeline_info'] = f.read()
    
    # Add the coverage report
    coverage_report = scout_configs.get('coverage_report', None)
    if coverage_report:
      mongo_case['coverage_report_path'] = coverage_report
    
    clinical_gene_lists = []
    research_gene_lists = []
    
    for gene_list in scout_configs.get('gene_lists', {}):
      list_info = scout_configs['gene_lists'][gene_list]
      
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
        clinical_gene_lists.append(list_object)
      else:
        research_gene_lists.append(list_object)

    mongo_case['clinical_gene_lists'] = clinical_gene_lists
    mongo_case['research_gene_lists'] = research_gene_lists

    individuals = []
    default_gene_lists = set()
    for individual in case['individuals']:
      # Get info from configs for the individual
      config_info = scout_configs.get(
                                  'individuals', {}
                                  ).get(
                                  individual['individual_id'], {}
                                  )
      ind = Individual()
      ind['father'] = individual['father']
      ind['mother'] = individual['mother']
      ind['display_name'] = individual['individual_id']
      ind['sex'] = str(individual['sex'])
      ind['phenotype'] = individual['phenotype']
      ind['individual_id'] = individual['individual_id']
      # Path to the bam file for IGV:
      ind['bam_file'] = config_info.get('bam_path', '')

      ind['capture_kits'] = config_info.get('capture_kit', [])

      for clinical_db in individual.get('extra_info', {}).get('Clinical_db', '').split(','):
        default_gene_lists.add(clinical_db)

      individuals.append(ind)

    mongo_case['individuals'] = individuals
    mongo_case['default_gene_lists'] = list(default_gene_lists)

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
    print("Please provide a ped file.(Use flag '-ped/--ped_file')", file=sys.stderr)
    sys.exit(0)
  
  mongo_case = get_case(setup_configs, family_type)
  print(mongo_case.to_json())
  
if __name__ == '__main__':
    cli()
