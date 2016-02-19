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



from __future__ import (absolute_import, print_function, division)

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

# from .config_parser import ConfigParser
# from .utils import (get_case, get_institute, get_mongo_variant)
# from scout.models import (Institute, Case, Variant)
# from scout._compat import iteritems

from vcf_parser import VCFParser

import scout

logger = logging.getLogger(__name__)

def load_mongo_db(scout_configs, vcf_configs=None, family_type='cmms',
                  mongo_db='variantDatabase', variant_type='clinical',
                  username=None, password=None, port=27017, host='localhost',
                  rank_score_threshold = 0, variant_number_threshold = 5000):
  """Populate a moongo database with information from ped and variant files."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])

  ####### Check if the vcf file is on the proper format #######
  vcf_file = scout_configs['load_vcf']
  logger.info("Found a vcf for loading variants into scout: {0}".format(
    vcf_file
  ))

  logger.info("Connecting to {0}".format(mongo_db))
  connect(mongo_db, host=host, port=port, username=username,
          password=password)

  variant_database = get_db()

  ped_file = scout_configs['ped']
  logger.info("Found a ped file: {0}".format(ped_file))

  ######## Parse the config file to check for keys ########
  logger.info("Parsing config file")
  config_object = ConfigParser(vcf_configs)

  ######## Get the cases and add them to the mongo db: ########

  logger.info("Get the case from ped file")
  case = get_case(scout_configs, family_type)

  logger.info('Case found in {0}: {1}'.format(ped_file, case.display_name))

  ######## Add the institute to the mongo db: ########

  for institute_name in case['collaborators']:
    if institute_name:
      institute = get_institute(institute_name)
      logger.info("Institute found: {0}".format(institute))
      try:
        Institute.objects.get(internal_id = institute.internal_id)
        logger.info("Institute {0} already in database".format(institute))
      except DoesNotExist:
        institute.save()
        logger.info("Adding new institute {0} to database".format(institute))

  logger.info("Updating case in database")

  update_case(case, variant_type)

  ######## Get the variants and add them to the mongo db: ########

  logger.info("Setting up a variant parser")
  variant_parser = VCFParser(infile=vcf_file)
  nr_of_variants = 0

  logger.info("Deleting old variants for case {0}".format(case.case_id))
  Variant.objects(case_id=case.case_id, variant_type=variant_type).delete()
  logger.debug("Variants deleted")

  start_inserting_variants = datetime.now()

  # Get the individuals to see which we should include in the analysis
  ped_individuals = {individual.individual_id: individual.display_name
                     for individual in case.individuals}

  # Check which individuals that exists in the vcf file.
  # Save the individuals in a dictionary with individual ids as keys
  # and display names as values
  individuals = {}
  # loop over keys (internal ids)
  logger.info("Checking which individuals in ped file exists in vcf")
  for individual_id, display_name in iteritems(ped_individuals):
    logger.debug("Checking individual {0}".format(individual_id))
    if individual_id in variant_parser.individuals:
      logger.debug("Individual {0} found".format(individual_id))
      individuals[individual_id] = display_name
    else:
        logger.warning("Individual {0} is present in ped file but"\
                      " not in vcf".format(individual_id))

  logger.info('Start parsing variants')

  ########## If a rank score threshold is used check if it is below that threshold ##########
  for variant in variant_parser:
    logger.debug("Parsing variant {0}".format(variant['variant_id']))
    if not float(variant['rank_scores'][case.display_name]) > rank_score_threshold:
      logger.info("Lower rank score threshold reaced after {0}"\
                  " variants".format(nr_of_variants))
      break

    if nr_of_variants > variant_number_threshold:
      logger.info("Variant number threshold reached. ({0})".format(
        variant_number_threshold))
      break


    nr_of_variants += 1
    mongo_variant = get_mongo_variant(variant, variant_type, individuals, case, config_object, nr_of_variants)

    mongo_variant.save()

    if nr_of_variants % 1000 == 0:
      logger.info('{0} variants parsed'.format(nr_of_variants))

  logger.info("Parsing variants done")
  logger.info("{0} variants inserted".format(nr_of_variants))
  logger.info("Time to insert variants: {0}".format(
    datetime.now() - start_inserting_variants
  ))

  logger.info("Updating indexes")

  ensure_indexes(variant_database, logger)

  return

def update_case(case, variant_type):
  """
  Update a case in in the mongo database.

  If a case is already existing (in case of a rerun), we need to update
  the existing one in a correct manner.

  Othervise insert the case.

  Arguments:
    case (Case): A case object.
    variant_type (str): 'research' or 'clinical'
  """
  case_id = case.case_id
  try:
    existing_case = Case.objects.get(case_id=case_id)
    logger.info("Case {0} already in database".format(case_id))
    if variant_type=='research':
      logger.info("Updating research gene list for case {0} to {1}".format(
        case_id, case.research_panels
      ))
      existing_case.research_panels = case.research_panels
      logger.info("Setting case {0} in research mode".format(case_id))
      existing_case.is_research = True
    else:
      logger.info("Updating clinical gene list for case {0} to {1}".format(
        case_id, case.clinical_panels
      ))
      existing_case.clinical_panels = case.clinical_panels
    logger.info("Updating individuals for case {0} to {1}".format(
      case_id, case.individuals
    ))
    existing_case.individuals = case.individuals
    logger.info("Updating time for case {0}".format(case_id))
    existing_case.updated_at = case.updated_at

    # This decides which gene lists that should be shown when the case is opened
    logger.info("Updating default gene lists for case {0} to {1}".format(
      case_id, case.default_panels
    ))
    existing_case.default_panels = case.default_panels

    logger.info("Updating genome build for case {0} to {1}".format(
      case_id, case.genome_build
    ))
    existing_case.genome_build = case.genome_build
    logger.info("Updating genome version for case {0} to {1}".format(
      case_id, case.genome_version
    ))
    existing_case.genome_version = case.genome_version
    logger.info("Updating analysis date for case {0} to {1}".format(
      case_id, case.analysis_date
    ))

    existing_case.analysis_date = case.analysis_date

    # madeline info is a full xml file
    logger.info("Updating madeline file for case {0}".format(case_id))
    existing_case.madeline_info = case.madeline_info
    existing_case.vcf_file = case.vcf_file
    logger.info("Updating vcf file for case {0} to {1}".format(
      case_id, case.vcf_file
    ))

    if case.coverage_report:
      existing_case.coverage_report = case.coverage_report
    logger.info("Updating coverage report for case {0}".format(case_id))

    existing_case.save()

  except DoesNotExist:
    logger.info('New case!')
    case.save()

  return

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

def ensure_indexes(variant_database, logger):
  """
  Update all the necessary indexes.

  Arguments:
    variant_database (db_communicator)
    logger (logging.logger)
  """

  variant_collection = variant_database['variant']
  logger.info("Updating first compound index")
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
  logger.info("Updating index with hgnc symbols and exac frequency")
  variant_collection.ensure_index(
                [
                  ('hgnc_symbols', ASCENDING),
                  ('exac_frequency', ASCENDING),
                ],
                background=True
      )

  logger.info("Updating index with 1000G frequency, functional annotation"\
              " and region annotation.")
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
@click.option('-l', '--logfile',
                    type=click.Path(exists=False),
                    help="Path to log file. If none logging is "\
                          "printed to stderr."
)
@click.option('--loglevel',
                    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                        'CRITICAL']),
                    help="Set the level of log output."
)
def cli(vcf_file, ped_file, vcf_config_file, scout_config_file, family_type,
        mongo_db, username, variant_type, madeline, password, institute,
        rank_score_threshold, variant_number_threshold,
        logfile, loglevel):
  """Test the vcf class."""
  # Check if vcf file exists and that it has the correct naming:
  from pprint import pprint as pp
  from ...log import init_log

  logger = logging.getLogger("scout")
  init_log(logger, logfile, loglevel)

  base_path = os.path.abspath(os.path.join(os.path.dirname(scout.__file__), '..'))

  scout_validation_file = os.path.join(base_path, 'config_spec/scout_config.ini')
  if not vcf_config_file:
    vcf_config_file = os.path.join(base_path, 'configs/vcf_config.ini')
  mongo_configs = os.path.join(base_path, 'instance/scout.cfg')

  setup_configs = {}

  if scout_config_file:
    setup_configs = ConfigParser(scout_config_file, configspec=scout_validation_file)

  if vcf_file:
    setup_configs['load_vcf'] = vcf_file

  if ped_file:
    setup_configs['ped'] = ped_file

  if madeline:
    setup_configs['madeline'] = madeline

  if institute:
    setup_configs['institutes'] = [institute]

  if not setup_configs.get('load_vcf', None):
    logger.warning("Please provide a vcf file.(Use flag '-vcf/--vcf_file')")
    sys.exit(0)

  # Check that the ped file is provided:
  if not setup_configs.get('ped', None):
    logger.warning("Please provide a ped file.(Use flag '-ped/--ped_file')")
    sys.exit(0)

  # Check that the config file is provided:
  if not vcf_config_file:
    logger.warning("Please provide a vcf config file.(Use flag '-vcf_config/--vcf_config_file')")
    sys.exit(0)

  my_vcf = load_mongo_db(setup_configs, vcf_config_file, family_type,
                      mongo_db=mongo_db, username=username, password=password,
                      variant_type=variant_type,
                      rank_score_threshold=rank_score_threshold,
                      variant_number_threshold=variant_number_threshold)


if __name__ == '__main__':
  cli()
