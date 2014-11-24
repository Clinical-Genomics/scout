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
  
  
  ######## Get the variants and add them to the mongo db: ########
  
  individuals = [individual.individual_id for individual in case.individuals]
  
  variant_parser = vcf_parser.VCFParser(infile = vcf_file)
  nr_of_variants = 0
  
  start_inserting_variants = datetime.now()
  
  for variant in variant_parser:
    nr_of_variants += 1
    mongo_variant = get_variant(variant, individuals, case['case_id'], config_object, nr_of_variants)
    mongo_variant.save()
  
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
    ind['sex'] = str(individual['sex'])
    ind['phenotype'] = individual['phenotype']
    ind['individual_id'] = individual['individual_id']
    ind['capture_kit'] = individual.get('extra_info', {}).get('Capture_kit', '').split(',')
    for clinical_db in individual.get('extra_info', {}).get('Clinical_db', '').split(','):
      databases.add(clinical_db)
    individuals.append(ind)
  mongo_case['individuals'] = individuals
  mongo_case['databases'] = list(databases)
  
  return mongo_case

def get_variant(variant, individuals, case_id, config_object, variant_count):
  """Return the variant in a format specified for scout. The structure is decided by the config file that is used."""


  def get_genotype_information(variant, genotype_collection, individual):
    """Get the genotype information in the proper format and return ODM specified gt call."""
    mongo_gt_call = GTCall(sample=individual)
    for genotype_information in genotype_collection:
      if config_object[genotype_information]['vcf_format_key'] == 'GT':
        mongo_gt_call['genotype_call'] = variant['genotypes'][individual].genotype
      elif config_object[genotype_information]['vcf_format_key'] == 'DP':
        mongo_gt_call['read_depth'] = variant['genotypes'][individual].depth_of_coverage
      elif config_object[genotype_information]['vcf_format_key'] == 'AD':
        mongo_gt_call['allele_depths'] = [variant['genotypes'][individual].ref_depth,
                                          variant['genotypes'][individual].alt_depth]
      elif config_object[genotype_information]['vcf_format_key'] == 'GQ':
        mongo_gt_call['genotype_quality'] = variant['genotypes'][individual].genotype_quality
    
    return mongo_gt_call
  
  
  id_fields = [variant['CHROM'], variant['POS'], variant['REF'], variant['ALT']]
  # We insert the family with the md5-key as id, same key we use in cases
  # Add the core information about the variant  
  mongo_variant = Variant(variant_id = generate_md5_key(id_fields),
                          display_name = '_'.join(id_fields),
                          chromosome = variant['CHROM'],
                          position = int(variant['POS']),
                          reference = variant['REF'],
                          alternatives = variant['ALT'].split(',')
                  )
  
  mongo_variant['db_snp_ids'] = variant.get(config_object['ID']['vcf_field'], '').split(
                                              config_object['ID']['vcf_data_field_separator'])
  
  mongo_common = VariantCommon()
  # Add the gene ids
  mongo_common['hgnc_symbols'] = variant['info_dict'].get(config_object['HGNC_symbol']['vcf_info_key'], '').split(
                                              config_object['HGNC_symbol']['vcf_data_field_separator'])
  mongo_common['ensemble_gene_ids'] = variant['info_dict'].get(config_object['Ensembl_gene_id']['vcf_info_key'], '').split(
                                              config_object['Ensembl_gene_id']['vcf_data_field_separator'])
  # Add the frequencies
  mongo_common['thousand_genomes_frequency'] = min([float(frequency) for frequency in
              variant['info_dict'].get(config_object['1000GMAF']['vcf_info_key'], '0').split(
              config_object['1000GMAF']['vcf_data_field_separator'])])
  
  mongo_common['exac_frequency'] = min([float(frequency) for frequency in
              variant['info_dict'].get(config_object['EXAC']['vcf_info_key'], '0').split(
              config_object['EXAC']['vcf_data_field_separator'])])

  # Add the severity predictions
  mongo_common['cadd_score'] = max([float(score) for score in
              variant['info_dict'].get(config_object['CADD']['vcf_info_key'], '0').split(
              config_object['CADD']['vcf_data_field_separator'])])
  
  mongo_common['sift_predictions'] = variant['info_dict'].get(config_object['Sift']['vcf_info_key'], '').split(
              config_object['Sift']['vcf_data_field_separator'])
  
  mongo_common['polyphen_predictions'] = variant['info_dict'].get(config_object['PolyPhen']['vcf_info_key'], '').split(
              config_object['PolyPhen']['vcf_data_field_separator'])
  
  # Add functional annotation
  mongo_common['functional_annotation'] = variant['info_dict'].get(config_object['FunctionalAnnotation']['vcf_info_key'], '').split(
              config_object['FunctionalAnnotation']['vcf_data_field_separator'])
  
  # Add region annotation
  mongo_common['region_annotation'] = variant['info_dict'].get(config_object['GeneticRegionAnnotation']['vcf_info_key'], '').split(
              config_object['GeneticRegionAnnotation']['vcf_data_field_separator'])
  
  # Add the common field:
  mongo_variant['common'] = mongo_common
  
  # Add the information that is specific to this case
  mongo_specific = VariantCaseSpecific()
  mongo_specific['rank_score'] = float(variant['info_dict'].get(config_object['RankScore']['vcf_info_key'], 0))
  mongo_specific['variant_rank'] = variant_count
  mongo_specific['quality'] = float(variant.get(config_object['QUAL']['vcf_field'], 0))
  mongo_specific['filters'] = variant.get(config_object['FILTER']['vcf_field'], '').split(
                                              config_object['FILTER']['vcf_data_field_separator'])
  
  # print('Genetic models:%s' % variant['info_dict'].get(config_object['GeneticModels']['vcf_info_key'], ''))
  
  mongo_specific['genetic_models'] = variant['info_dict'].get(config_object['GeneticModels']['vcf_info_key'], '').split(
                                              config_object['GeneticModels']['vcf_data_field_separator'])
  
  
  mongo_variant['specific'][case_id] = mongo_specific


  # Add the genotype information for each individual
  gt_calls = []
  for individual in individuals:
    # This function returns an ODM GTCall object with the relevant information:
    gt_calls.append(get_genotype_information(variant, config_object.categories['genotype_information'], individual))
  
  mongo_variant['specific'][case_id]['samples'] = gt_calls
  
  return mongo_variant


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
