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

from pymongo import MongoClient

from .config_parser import ConfigParser

from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

from pprint import pprint as pp


def load_mongo(vcf_file=None, ped_file=None, config_file=None):
  """Populate a moongo database with information from ped and variant files."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  
  client = MongoClient('localhost', 27017)
  db = client.variantDatabase
  # combine path to the local development fixtures
  project_root = '/vagrant/scout'
  # print(project_root, vcf_file, ped_file, config_file)
  config_object = ConfigParser(config_file)  
  
  # pp(config_object.__dict__)
  
  ######## Get the case and add it to the mongo db: ######## 
  cases = db.cases
  
  
  case = get_case(ped_file)
  # pp(case)
  
  case_individuals = [individual['individual_id'] for individual in case['individuals']]
  
  cases.insert(case)
  
  # print('Collections:\n')
  # pp(config_object.collections)
  # print('Categories:\n')
  # pp(config_object.categories)
  
  ######## Get the variants and add them to the mongo db: ######## 
  
  variants = db.variants
  
  # variants = {} # Dict like {case_id: variant_parser}
  variant_parser = vcf_parser.VCFParser(infile = vcf_file)
  for variant in variant_parser:
    # pp(variant)
    # pp(format_variant(variant, case, config_object))
    variants.insert(format_variant(variant, case, config_object))
    
  sys.exit()
  
  

def get_case(ped_file):
  """Take a case file and return the case on the specified format."""
  
  case_parser = ped_parser.FamilyParser(ped_file)
  case = case_parser.get_json()[0]
  
  return case
  
  
# def cases(self):
#   return self._cases
#
# def case(self, case_id):
#   for case in self._cases:
#     if case['id'] == case_id:
#       return case
#


def format_variant(variant, case, config_object):
  """Return the variant in a format specified for scout."""
  
  
  def generate_md5_key(chrom, pos, ref, alt):
    """Generate an md5-key from variant information"""
    h = hashlib.md5()
    alt = ','.join(alt)
    h.update(' '.join([chrom, pos, ref, alt]))
    return h.hexdigest()
  
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
    return value
  
  family_id = case['family_id']
  case_individuals = [individual['individual_id'] for individual in case['individuals']]
  
  formated_variant = {'common':{}, 'specific':{}}
  formated_variant['specific'][family_id] = {}
  formated_variant['specific'][family_id]['samples'] = []
  
  formated_variant['variant_id'] = variant['variant_id']
  formated_variant['md5_key'] = generate_md5_key(variant['CHROM'], variant['POS'], variant['REF'], variant['ALT'])
  
  
  # Add the genotype information for each individual 
  for individual in case_individuals:
    formated_variant['specific'][family_id]['samples'].append(
          get_genotype_information(variant, config_object.categories['genotype_information'], individual))
  
  for annotation in config_object.collections['core']:
    # print('core', annotation)
    formated_variant[config_object[annotation]['internal_record_key']] = get_value(variant, 'core', annotation)
  
  for annotation in config_object.collections['common']:
    # print('common', annotation)
    formated_variant['common'][config_object[annotation]['internal_record_key']] = get_value(variant, 'common', annotation)
  
  for annotation in config_object.collections['case']:
    # print('common', annotation)
    formated_variant['specific'][family_id][config_object[annotation]['internal_record_key']] = get_value(variant, 'case', annotation)
  
  # for category in config_object.categories:
  #   for member in config_object.categories[category]:
  #     if category != 'config_info':
  #       if config_object[member]['collection'] == 'core':
  #         formated_variant[config_object[member]['internal_record_key']] = get_value(variant, category, member)
  #
  #       elif config_object[member]['collection'] == 'common':
  #         formated_variant['common'][config_object[member]['internal_record_key']] = get_value(variant, category, member)
  #
  #       elif config_object[member]['collection'] == 'case':
  #         # Consider to use default dict here...
  #         if family_id not in formated_variant['specific']:
  #           formated_variant['specific'][family_id] = {}
  #         for individual in case_individuals:
  #           formated_variant['specific'][family_id][config_object[member]['internal_record_key']] = get_value(
                                                                                                # variant, category, member, )
          # else:
  
  return formated_variant
  
  
def variants(self, case, query=None, variant_ids=None, nr_of_variants = 100, skip = 0):

  # if variant_ids:
  #   return self._many_variants(variant_ids)

  variants = []
  nr_of_variants = skip + nr_of_variants
  i = 0
  for variant in vcf_parser.VCFParser(infile = self._variants[case]):
    if i > skip:
      if i < nr_of_variants:
        yield self.format_variant(variant)
      else:
        return
    i += 1
  return

# def _many_variants(self, variant_ids):
#   variants = []
#
#   for variant in self._variants:
#     if variant['id'] in variant_ids:
#       variants.append(variant)
#
#   return variants

# def variant(self, variant_id):
#   for variant in self._variants:
#     if variant['variant_id'] == variant_id:
#       return self.format_variant(variant)
#
#   return None

# def create_variant(self, variant):
#   # Find out last ID
#   try:
#     last_id = self._variants[-1]['id']
#   except IndexError:
#     last_id = 0
#
#   next_id = last_id + 1
#
#   # Assign id to the new variant
#   variant['id'] = next_id
#
#   # Add new variant to the list
#   self._variants.append(variant)
#
#   return variant

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
# @click.argument('outfile',
#                 nargs=1,
#                 type=click.File('w')
# )
def cli(vcf_file, ped_file, config_file):
  """Test the vcf class."""
  my_vcf = load_mongo(vcf_file, ped_file, config_file)
  # my_vcf.init_app('app', vcf_dir, config_file)
  
  # for case in my_vcf.cases():
  #   pp(case)
  # print('')
  
  # for case in my_vcf._cases:
  #   for variant in my_vcf.variants(case['id']):
  #     pp(variant)
  #   print('')
  # for root, dirs, files in os.walk(cases_path):
  #   if files:
  #     ped_file = None
  #     vcf_file = None
  #     zipped_vcf_file = None
  #     case = None
  #     for file in files:
  #       if os.path.splitext(file)[-1] == '.ped':
  #         ped_file = os.path.join(root, file)
  #         case_parser = ped_parser.FamilyParser(ped_file)
  #         case = case_parser.get_json()[0]
  #       if os.path.splitext(file)[-1] == '.vcf':
  #         vcf_file = os.path.join(root, file)
  #       if os.path.splitext(file)[-1] == '.gz':
  #         if os.path.splitext(file)[0][-1] == '.gz':
  #           zipped_vcf_file = os.path.join(root, file)
  #     # If no vcf we search for zipped files
  #     if not vcf_file:
  #       vcf_file = zipped_vcf_file
  #     # If ped and vcf are not found exit:
  #     if not (ped_file and vcf_file):
  #       raise SyntaxError('Wrong folder structure in vcf directories. '
  #                         'Could not find ped and/or vcf files. '
  #                           'See documentation.')
  #     # Store the path to variants as case id:s:
  #     case['id'] = case['family_id']
  #     case['vcf_path'] = vcf_file
    

if __name__ == '__main__':
    cli()
