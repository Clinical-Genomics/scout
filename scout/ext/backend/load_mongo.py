#!/usr/bin/env python
# encoding: utf-8
"""
load_mongo.py

Load script for the mongo db.
Should take a directory as input, like the load part of vcf.py, and populate the mongo database.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

# Questions for Mats:
# - Should we first check if variant is in database and then update?
# - Is it more effective to, like in sql, update the database with alot of data at the same time or can we do one and one?
# - How to handle general and specific?
# - How to initiate an index on a field?
# - What does this pymongo.ASCENDING means?



from __future__ import (absolute_import, unicode_literals, print_function,
                        division)
import sys
import os
import io
import json
import click
import logging

from datetime import datetime
from pymongo import (ASCENDING, DESCENDING)
from mongoengine import connect, DoesNotExist
from mongoengine.connection import get_db

from .config_parser import ConfigParser
from .utils import (get_case, get_institute, get_mongo_variant)
from ...models import (Institute, Case)
from ..._compat import iteritems
from ....log import init_log


from vcf_parser import VCFParser

from pprint import pprint as pp

import scout


def load_mongo_db(scout_configs, config_file=None, family_type='cmms',
                  mongo_db='variantDatabase', variant_type='clinical',
                  username=None, password=None, port=27017,
                  rank_score_treshold = 0, host='localhost',verbose = False,
                  log_file=None, log_level=None):
  """Populate a moongo database with information from ped and variant files."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  logger = logging.getLogger(__name__)
  init_log(logger, logfile, loglevel)
  
  ####### Check if the vcf file is on the proper format #######
  vcf_file = scout_configs['load_vcf']
  splitted_vcf_file_name = os.path.splitext(vcf_file)
  vcf_ending = splitted_vcf_file_name[-1]
  if vcf_ending != '.vcf':
    if vcf_ending == '.gz':
      vcf_ending = os.path.splitext(splitted_vcf_file_name)[-1]
      if vcf_ending != '.vcf':
        logger.error("Please use the correct prefix of your vcf file"\
                        "('.vcf/.vcf.gz')")
        raise Exception
    else:
      if vcf_ending != '.vcf':
        logger.error("Please use the correct prefix of your vcf file('.vcf/.vcf.gz')")
        raise Exception
  
  logger.info("Connecting to {0}".format(mongo_db))
  connect(mongo_db, host=host, port=port, username=username,
          password=password)

  variant_database = get_db()

  ped_file = scout_configs['ped']
  
  logger.info("Starting to load database with:"\
              "\nvcf_file:\t{0}\nped_file:\t{1}\nconfig_file:\t{2}\n"\
              "family_type:\t{3}\nmongo_db:\t{4}\ninstitutes:\t{5}\n".format(
                vcf_file, ped_file, config_file, family_type, mongo_db, 
                ','.join(scout_configs['institutes'])))

  ######## Parse the config file to check for keys ########
  logger.info("Parsing config file")
  config_object = ConfigParser(config_file)

  ######## Add the institute to the mongo db: ########

  # institutes is a list with institute objects
  institutes = []
  for institute_name in scout_configs['institutes']:
    institutes.append(get_institute(institute_name))
  logger.info("Institutes found: {0}".format(institutes))
  
  # If the institute exists we work on the old one
  for i, institute in enumerate(institutes):
    try:
      if Institute.objects.get(internal_id = institute.internal_id):
        institutes[i] = Institute.objects.get(internal_id = institute.internal_id)
    except DoesNotExist:
        logger.info('New institute!')

  ######## Get the cases and add them to the mongo db: ########

  logger.info("Get the cases from ped file")
  case = get_case(scout_configs, family_type)

  logger.info('Case found in {0}: {1}'.format(ped_file, case.display_name))

  # Add the case to its institute(s)
  logger.info("Adding cases to the institutes")
  for institute_object in institutes:
    if case not in institute_object.cases:
      institute_object.cases.append(case)
      logger.debug("Adding {0} to {1}".format(case, institute_object.internal_id))
  
    institute_object.save()

  try:
    existing_case = Case.objects.get(case_id = case.case_id)
    if variant_type=='research':
      existing_case.research_gene_lists = case.research_gene_lists
      existing_case.is_research = True
    else:
      existing_case.clinical_gene_lists = case.clinical_gene_lists
    existing_case.save()
  except DoesNotExist:
    logger.info('New case!')
    case.save()

  ######## Get the variants and add them to the mongo db: ########
  
  logging.info("Setting up a variant parser")
  variant_parser = VCFParser(infile=vcf_file, split_variants=True)
  nr_of_variants = 0
  start_inserting_variants = datetime.now()

  # Get the individuals to see which we should include in the analysis
  ped_individuals = {individual.individual_id: individual.display_name
                     for individual in case.individuals}

  # Check which individuals that exists in the vcf file.
  # Save the individuals in a dictionary with individual ids as keys
  # and display names as values
  individuals = {}
  # loop over keys (internal ids)
  for individual_id, display_name in iteritems(ped_individuals):
    if individual_id in variant_parser.individuals:
      individuals[individual_id] = display_name
    else:
      if verbose:
        print("Individual %s is present in ped file but not in vcf!\n"
              "Continuing analysis..." % individual_id, file=sys.stderr)

  if verbose:
    print('Start parsing variants...', file=sys.stderr)

  ########## If a rank score treshold is used check if it is below that treshold ##########
  for variant in variant_parser:
    if not float(variant['rank_scores'][case.display_name]) > rank_score_treshold:
      break

    nr_of_variants += 1
    mongo_variant = get_mongo_variant(variant, variant_type, individuals, case, config_object, nr_of_variants)

    mongo_variant.save()

    if verbose:
      if nr_of_variants % 1000 == 0:
        print('%s variants parsed!' % nr_of_variants, file=sys.stderr)

  if verbose:
    print('%s variants inserted!' % nr_of_variants, file=sys.stderr)
    print('Time to insert variants: %s' % (datetime.now() - start_inserting_variants), file=sys.stderr)

  if verbose:
    print('Updating indexes...', file=sys.stderr)

  ensure_indexes(variant_database)

  return

def update_cases(case):
  """
  Update cases in the mongo database.
  
  If a case is already existing (in case of a rerun), we need to update
  the existing one in a correct manner.
  
  Othervise insert the case.
  
  Arguments:
    case (Case): A case object.
  """
  

def update_local_frequencies(variant_database):
  """
  Update the local frequencies for each variant in the database.

  For each document id in the database we find all variants with the same
  variant id. We count the number of variants and divide this number by the
  total number of cases.

  Args:
    variant_database  : A pymongo connection to the database

  """
  variant_collection = variant_database['variant']
  case_collection = variant_database['case']
  number_of_cases = case_collection.count()
  for variant in variant_collection.find():
    variant_id = variant['variant_id']
    variant['local_frequency'] = (variant_collection.find(
                                    {
                                        'variant_id':variant['variant_id']
                                    }
                                  ).count()) / number_of_cases
  return

def ensure_indexes(variant_database):
  """Function to check the necessary indexes."""
  variant_collection = variant_database['variant']
  variant_collection.ensure_index(
                [
                  ('case_id', ASCENDING),
                  ('variant_rank', ASCENDING),
                  ('variant_type', ASCENDING),
                  ('thousand_genomes_frequency', ASCENDING),
                  ('gene_lists', ASCENDING)
                ],
                background=True
      )
  variant_collection.ensure_index(
                [
                  ('hgnc_symbols', ASCENDING),
                  ('exac_frequency', ASCENDING),
                ],
                background=True
      )

  variant_collection.ensure_index(
                [
                  ('thousand_genomes_frequency', ASCENDING),
                  ('gene.functional_annotation', ASCENDING),
                  ('gene.region_annotation', ASCENDING)
                ],
                background=True
      )

@click.command()
@click.option('-f', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-p', '--ped_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
@click.option('--vcf_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the config file for loading the variants."
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
@click.option('-vt', '--variant_type',
                type=click.Choice(['clinical', 'research']),
                default='clinical',
                nargs=1,
                help="Specify the type of the variants that is being loaded."
)
@click.option('-i', '--institute',
                default='CMMS',
                nargs=1,
                help="Specify the institute that the file belongs to."
)
@click.option('-db', '--mongo-db',
                default='variantDatabase'
)
@click.option('-u', '--username',
                type=str
)
@click.option('-p', '--password',
                type=str
)
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(vcf_file, ped_file, vcf_config_file, scout_config_file, family_type,
        mongo_db, username, variant_type, madeline, password, institute,
        verbose):
  """Test the vcf class."""
  # Check if vcf file exists and that it has the correct naming:

  base_path = os.path.abspath(os.path.join(os.path.dirname(scout.__file__), '..'))
  mongo_configs = os.path.join(base_path, 'instance/scout.cfg')

  setup_configs = {}

  if scout_config_file:
    setup_configs = ConfigParser(scout_config_file)

  if vcf_file:
    setup_configs['load_vcf'] = vcf_file

  if ped_file:
    setup_configs['ped'] = ped_file

  if madeline:
    setup_configs['madeline'] = madeline

  if institute:
    setup_configs['institutes'] = [institute]

  if not setup_configs.get('load_vcf', None):
    print("Please provide a vcf file.(Use flag '-vcf/--vcf_file')", file=sys.stderr)
    sys.exit(0)

  # Check that the ped file is provided:
  if not setup_configs.get('ped', None):
    print("Please provide a ped file.(Use flag '-ped/--ped_file')", file=sys.stderr)
    sys.exit(0)

  # Check that the config file is provided:
  if not vcf_config_file:
    print("Please provide a config file.(Use flag '-vcf_config/--vcf_config_file')", file=sys.stderr)
    sys.exit(0)

  my_vcf = load_mongo_db(setup_configs, vcf_config_file, family_type,
                      mongo_db=mongo_db, username=username, password=password,
                      variant_type=variant_type, verbose=verbose)


if __name__ == '__main__':
    cli()
