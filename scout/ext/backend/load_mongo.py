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



from __future__ import absolute_import, unicode_literals, print_function

import sys
import os

import io
import json
import click
import hashlib

from datetime import datetime
from pymongo import MongoClient
from mongoengine import connect

from .config_parser import ConfigParser
from ...models import *

from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

from pprint import pprint as pp


def load_mongo(vcf_file=None, ped_file=None, config_file=None,
               family_type='ped', mongo_db='variantDatabase', institute = 'CMMS'):
  """Populate a moongo database with information from ped and variant files."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])

  connect(mongo_db, host='localhost', port=27017)
  # db = client[mongo_db]
  # combine path to the local development fixtures
  project_root = '/vagrant/scout'
  # print(project_root, vcf_file, ped_file, config_file)
  config_object = ConfigParser(config_file)
    
  ######## Get the case and add it to the mongo db: ########
  
  case = get_case(ped_file, family_type, institute)
  case.save()
  
  ######## Add the to the mongo db: ########
  
  institute = get_institute(institute)
  institute.save()
  
  sys.exit()
  # This function updates the cases collection if the specific family exists.
  # If the family exists a new object is inserted
  
  ######## Get the variants and add them to the mongo db: ########
  
  variant_parser = vcf_parser.VCFParser(infile = vcf_file)
  nr_of_variants = 0

  for variant in variant_parser:
    nr_of_variants += 1
    # pp(variant)
    variant = get_variant(variant, case, config_object, variant_collection, nr_of_variants)

  print('%s variants inserted!' % nr_of_variants)
  print('Time to insert variants: %s' % (datetime.now() - start_inserting_variants))

def generate_md5_key(list_of_arguments):
  """Generate an md5-key from a list of arguments"""
  h = hashlib.md5()
  h.update(' '.join(list_of_arguments))
  return h.hexdigest()


def get_institute(institute):
  """Return a institute object"""
  return Institute(internal_id=institute, display_name=institute)

def get_case(ped_file, family_type, institute):
  """Take a case file and return the case on the specified format."""

  case = {}
  case_parser = ped_parser.FamilyParser(ped_file, family_type=family_type)
  
  case = case_parser.get_json()[0]
  
  mongo_case = Case(case_id = generate_md5_key([institute, case['family_id']]))
  mongo_case['display_name'] = case['family_id']
  individuals = []
  databases = set()
  for individual in case['individuals']:
    ind = Individual()
    ind['father'] = individual['father']
    ind['mother'] = individual['mother']
    ind['display_name'] = individual['individual_id']
    # Fix this when ped_parser is updated:
    ind['sex'] = str(individual['sex:'])
    ind['phenotype'] = individual['phenotype']
    ind['individual_id'] = individual['individual_id']
    ind['capture_kit'] = individual.get('extra_info', {}).get('Capture_kit', '').split(',')
    # Fix this when ped_parser is updated:
    for clinical_db in individual.get('extra_info', {}).get('Clinical_db\n', '').split(','):
      databases.add(clinical_db)
    individuals.append(ind)
  mongo_case['individuals'] = individuals
  mongo_case['databases'] = list(databases)
  
  return mongo_case


def load_variant(variant, case, config_object, variant_collection, variant_count):
  """Load a variant into the database."""
  formated_variant = format_variant(variant, case, config_object)
  case_specific = formated_variant.pop('specific', {})
  case_specific['variant_rank'] = variant_count
  
  variant_collection.update({ '_id': formated_variant['_id']}, {"$set" : formated_variant}, upsert=True)
  
  variant_collection.update({ '_id': formated_variant['_id']}, {"$set" : {("specific.%s" % case['_id']) : case_specific}})

  return

def get_variant(variant, case, config_object):
  """Return the variant in a format specified for scout. The structure is decided by the config file that is used."""


  def get_genotype_information(variant, genotype_collection, individual):
    """Get the genotype information in the proper format and return an array with the individuals."""
    individual_information = {'sample':individual}
    for genotype_information in genotype_collection:
      if config_object[genotype_information]['vcf_format_key'] == 'GT':
        individual_information[config_object[genotype_information]['internal_record_key']] = variant['genotypes'][individual].genotype
      elif config_object[genotype_information]['vcf_format_key'] == 'DP':
        individual_information[config_object[genotype_information]['internal_record_key']] = variant['genotypes'][individual].depth_of_coverage
      elif config_object[genotype_information]['vcf_format_key'] == 'AD':
        individual_information[config_object[genotype_information]['internal_record_key']] = variant['genotypes'][individual].allele_depth
      elif config_object[genotype_information]['vcf_format_key'] == 'GQ':
        individual_information[config_object[genotype_information]['internal_record_key']] = variant['genotypes'][individual].genotype_quality
    return individual_information

  def get_value(variant, collection, information):
    """Return the correct value from the variant according to rules in config parser.
        vcf_fiels can be one of the following[CHROM, POS, ID, REF, ALT, QUAL, INFO, FORMAT, individual, other]"""
    # If information is on the core we can access it directly through the vcf key
    value = None
    # The core information can be read straight from the vcf line
    if collection == 'core':
      value = variant[config_object[information]['vcf_field']]
    # The common data is read from the INFO field
    elif collection == 'common':
      value = variant['info_dict'].get(config_object[information]['vcf_info_key'], None)
    # The case specific information can be either in INFO field or one of the mandatory fields:
    elif collection == 'case':
      if config_object[information]['vcf_field'] == 'INFO':
        value = variant['info_dict'].get(config_object[information]['vcf_info_key'], None)
      else:
        value = variant.get(config_object[information]['vcf_field'], None)
    # Check if we should return a list:
    if value and config_object[information]['vcf_data_field_number'] != '1':
      value = value.split(config_object[information]['vcf_data_field_separator'])
    # If there should be one value but there are several we need to get the right one.
    # elif len(value.split(config_object[information].get(['vcf_data_field_separator'], ','))) > 1:

    return value

  # We insert the family with the md5-key as id, same key we use in cases
  variant_id = generate_md5_key([variant['CHROM'], variant['POS'], variant['REF'], variant['ALT']])
  # These are the individuals included in the family
  case_individuals = [individual['individual_id'] for individual in case['individuals']]

  # We use common to store annotations and specific to store
  formated_variant = {'common':{}, 'specific':{}}

  # Store the case specific variant information in specific:
  formated_variant['specific']['samples'] = []

  # Add the human readable display name to the variant
  formated_variant['display_name'] = variant['variant_id']

  formated_variant['_id'] = variant_id


  # Add the genotype information for each individual
  for individual in case_individuals:
    formated_variant['specific']['samples'].append(
          get_genotype_information(variant, config_object.categories['genotype_information'], individual))

  for annotation in config_object.collections['core']:
    formated_variant[config_object[annotation]['internal_record_key']] = get_value(variant, 'core', annotation)

  for annotation in config_object.collections['common']:
    formated_variant['common'][config_object[annotation]['internal_record_key']] = get_value(variant, 'common', annotation)

  for annotation in config_object.collections['case']:
    formated_variant['specific'][config_object[annotation]['internal_record_key']] = get_value(variant, 'case', annotation)

  return formated_variant


@click.command()
@click.argument('vcf_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.argument('ped_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.argument('config_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.option('-type', '--family_type',
                default='ped',
                nargs=1,
)
@click.option('-db', '--mongo-db', default='variantDatabase')
def cli(vcf_file, ped_file, config_file, family_type, mongo_db):
  """Test the vcf class."""
  my_vcf = load_mongo(vcf_file, ped_file, config_file, family_type,
                      mongo_db=mongo_db)


if __name__ == '__main__':
    cli()
