#!/usr/bin/env python
# encoding: utf-8
"""
mongo.py

This is the mongo adapter for scout, it is a communicator for quering and updating the mongodatabase.
Implements BaseAdapter.

Created by Måns Magnusson on 2014-11-17.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""
from __future__ import absolute_import, unicode_literals, print_function

import sys
import os

import io
import json
import click
from pymongo import MongoClient
import pymongo


from . import BaseAdapter
from .config_parser import ConfigParser

from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

from pprint import pprint as pp

class MongoAdapter(BaseAdapter):
  """Adapter for cummunication between the scout server and a mongo database."""

  def init_app(self, app):
    config = getattr(app, 'config', {})

    self.client = MongoClient(config.get('MONGODB_HOST', 'localhost'), config.get('MONGODB_PORT', 27017))
    self.db = self.client[config.get('MONGODB_DB', 'variantDatabase')]
    self.case_collection = self.db.cases
    self.variant_collection = self.db.variants

  def __init__(self, app=None):

    if app:
      self.init_app(app)
    
    # combine path to the local development fixtures
    # self.config_object = ConfigParser(config_file)


  def cases(self):
    for case in self.case_collection.find():
      yield case

  def case(self, case_id):

    return self.case_collection.find_one({ '_id' : case_id })


  def format_variant(self, variant, case_id):
    """Return the variant in a format specified for scout."""

    # Stupid solution to follow scout.models.py

    ### Core information ###

    formated_variant = {}
    formated_variant['common'] = {}
    formated_variant['specific'] = {}
    formated_variant['id'] = variant['_id']
    formated_variant['chromosome'] = variant['chromosome']
    formated_variant['position'] = variant['position']
    formated_variant['reference'] = variant['reference']
    formated_variant['alternatives'] = variant['alternatives']
    formated_variant['display_name'] = variant['display_name']

    ### Specific information ###

    # Gene ids:
    formated_variant['common']['hgnc_symbols'] = variant['common'].get('hgnc_symbols', [])
    formated_variant['common']['ensemble_gene_ids'] = variant['common'].get('ensemble_gene_ids', [])
    # Frequencies:
    formated_variant['common']['thousand_genomes_frequency'] = variant['common'].get('thousand_genomes_frequency', None)
    formated_variant['common']['exac_frequency'] = variant['common'].get('exac_frequency', None)
    # Predicted deleteriousness:
    formated_variant['common']['cadd_score'] = variant['common'].get('cadd_score', None)
    formated_variant['common']['sift_predictions'] = variant['common'].get('sift_predictions', [])
    formated_variant['common']['polyphen_predictions'] = variant['common'].get('polyphen_predictions', [])
    formated_variant['common']['functional_annotation'] = variant['common'].get('functional_annotation', [])
    formated_variant['common']['region_annotation'] = variant['common'].get('region_annotation', [])

    ### Specific information ###

    formated_variant['specific']['rank_score'] = variant['specific'][case_id].get('rank_score', 0)
    formated_variant['specific']['filters'] = variant['specific'][case_id].get('filters', [])
    formated_variant['specific']['genetic_models'] = variant['specific'][case_id].get('genetic_models', [])
    formated_variant['specific']['quality'] = variant['specific'][case_id].get('quality', 0.0)
    formated_variant['specific']['variant_rank'] = variant['specific'][case_id].get('variant_rank', 0)
    formated_variant['specific']['samples'] = variant['specific'][case_id].get('samples', [])

    return formated_variant


  def variants(self, case_id, query=None, variant_ids=None, nr_of_variants = 10, skip = 0):

    # if variant_ids:
    #   return self._many_variants(variant_ids)

    variants = []
    nr_of_variants = skip + nr_of_variants
    case_specific = ('specific.%s' % case_id)
    for variant in self.variant_collection.find({case_specific: {'$exists' : True}}).sort(case_specific + '.variant_rank', pymongo.ASCENDING)[skip:nr_of_variants]:
      # yield variant
      yield self.format_variant(variant, case_id)


  def variant(self, variant_id):

    return self.format_variant(self.variant_collection.find_one({ '_id' : variant_id}))


  def next_variant(self, variant_id, case_id):
    """Returns the next variant from the rank order"""
    case_specific = ('specific.%s' % case_id)
    previous_variant = self.variant_collection.find_one({'_id': variant_id})
    rank = int(previous_variant['specific'].get(case_id, {}).get('variant_rank', 0))
    
    return self.format_variant(self.variant_collection.find_one(
                {case_specific + '.variant_rank': rank+1}), case_id)
    
  def previous_variant(self, variant_id, case_id):
    """Returns the next variant from the rank order"""
    case_specific = ('specific.%s' % case_id)
    previous_variant = self.variant_collection.find_one({'_id': variant_id})
    rank = int(previous_variant['specific'].get(case_id, {}).get('variant_rank', 0))
    
    return self.format_variant(self.variant_collection.find_one(
                {case_specific + '.variant_rank': rank-1}), case_id)
  
  def create_variant(self, variant):
    # Find out last ID
    try:
      last_id = self._variants[-1]['id']
    except IndexError:
      last_id = 0

    next_id = last_id + 1

    # Assign id to the new variant
    variant['id'] = next_id

    # Add new variant to the list
    self._variants.append(variant)

    return variant

  def add_synopsis(self, case_id, synopsis):
    """Add a synopsis string to a case"""
    self.case_collection.update({'_id': case_id}, {'$set' : {'synopsis' : synopsis}})
    return

@click.command()
# @click.argument('vcf_dir',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
# @click.argument('ped_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
# @click.argument('config_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
# @click.argument('outfile',
#                 nargs=1,
#                 type=click.File('w')
# )
def cli():
    """Test the vcf class."""
    import hashlib

    def generate_md5_key(list_of_arguments):
      """Generate an md5-key from a list of arguments"""
      h = hashlib.md5()
      h.update(' '.join(list_of_arguments))
      return h.hexdigest()

    my_mongo = MongoAdapter(app='hej')

    ### FOR DEVELOPMENT ###
    small_family_id = generate_md5_key(['3'])
    big_family_id = generate_md5_key(['2'])
    # for case in my_mongo.cases():
    #   variant_count = 0
    #   pp(case)
      # for variant in my_mongo.variants(case['_id'], nr_of_variants = 20):
      #   pp(variant)
      #   variant_count += 1
      #   print(variant_count)
    # my_vcf.init_app('app', vcf_dir, config_file)
    # rank = my_mongo.next_variant('0ab656e8fe4aaf8f87405a0bc3b18eba', 'a684eceee76fc522773286a895bc8436')
    pp(my_mongo.next_variant('0ab656e8fe4aaf8f87405a0bc3b18eba', 'a684eceee76fc522773286a895bc8436'))
    # print(rank, type(rank))
    # for case in my_vcf.cases():
    #   pp(case)
    # print('')

    # for case in my_vcf._cases:
    #   for variant in my_vcf.variants(case['id']):
    #     pp(variant)
    #   print('')

if __name__ == '__main__':
    cli()
