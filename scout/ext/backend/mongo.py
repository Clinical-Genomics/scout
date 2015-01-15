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
from mongoengine import connect, DoesNotExist

from . import BaseAdapter
from .config_parser import ConfigParser
from ...models import (Variant, Compound, Case)


from pprint import pprint as pp

class MongoAdapter(BaseAdapter):
  """Adapter for cummunication between the scout server and a mongo database."""

  def init_app(self, app):
    config = getattr(app, 'config', {})

    # self.client = MongoClient(config.get('MONGODB_HOST', 'localhost'), config.get('MONGODB_PORT', 27017))
    # self.db = self.client[config.get('MONGODB_DB', 'variantDatabase')]
    host = config.get('MONGODB_HOST', 'localhost')
    port = config.get('MONGODB_PORT', 27017)
    database = config.get('MONGODB_DB', 'variantDatabase')
    username = config.get('MONGODB_USERNAME', None)
    password = config.get('MONGODB_PASSWORD', None)

    connect(database, host=host, port=port, username=username,
            password=password)

    # self.case_collection = self.db.case
    # self.variant_collection = self.db.variant

  def __init__(self, app=None):

    if app:
      self.init_app(app)

    # combine path to the local development fixtures
    # self.config_object = ConfigParser(config_file)


  def cases(self):
    return Case.objects

  def case(self, case_id):

    try:
      return Case.objects(case_id = case_id)
    except DoesNotExist:
      return None

  def format_variant(self, variant):
    """Return a variant where relevant information is added."""
    for case in variant['specific']:
      case_specific = ('specific.%s' % case)
      for compound in variant['specific'][case]['compounds']:
        # print('Compound id: %s, Display name: %s, Combined_score: %s' %
        #         (compound['variant_id'], compound['display_name'], compound['combined_score']))
        try:
          pair = Variant.objects.get(pk = compound['variant_id'])
          compound['functional_annotations'] = pair['common']['functional_annotations']
          compound['region_annotations'] = pair['common']['region_annotations']
        except DoesNotExist:
          pass
    return variant

  def variants(self, case_id, query=None, variant_ids=None, nr_of_variants = 10, skip = 0):
    """
    Returns the number of variants specified in question for a specific case.
    If skip ≠ 0 skip the first n variants.
    
    Arguments:
      case_id : A string that represents the case
      query   : A dictionary with querys for the database
      
    Returns:
      A generator with the variants
      
    """
    
    nr_of_variants = skip + nr_of_variants
    # for variant in Variant.objects(__raw__ = {case_specific: {'$exists' : True}}).order_by(
    #                                   case_specific + '.variant_rank')[skip:nr_of_variants]:
    for variant in Variant.objects(case_id = case_id):
      yield variant

  def variant(self, document_id):
    """
    Returns the specified variant.
    
    Arguments:
      document_id : A md5 key that represents the variant
    
    Returns:
      variant_object: A odm variant object
    """
    
    try:
      return Variant.objects(document_id = document_id)
    except DoesNotExist:
      return None

  def next_variant(self, document_id):
    """
    Returns the next variant from the rank order.
    
    Arguments:
      document_id : A md5 key that represents the variant
    
    Returns:
      variant_object: A odm variant object
    """
    
    previous_variant = Variant.objects(document_id=document_id)
    rank = previous_variant.variant_rank or 0
    case_id = previous_variant.case_id
    try:
      return Variant.objects(Q(case_id= case_id) & Q(variant_rank = rank+1))
    except DoesNotExist:
      return None

  def previous_variant(self, document_id):
    """
    Returns the next variant from the rank order
    
    Arguments:
      document_id : A md5 key that represents the variant
    
    Returns:
      variant_object: A odm variant object
    
    """
    previous_variant = Variant.objects(document_id=document_id)
    rank = previous_variant.variant_rank or 0
    case_id = previous_variant.case_id
    try:
      return Variant.objects(Q(case_id= case_id) & Q(variant_rank = rank-1))
    except DoesNotExist:
      return None
    
@click.command()
@click.option('-i','--institute',
                default='CMMS'
)
@click.option('-c' ,'--case',
                default='1'
)
@click.option('--thousand_g',
                default=100.0
)
@click.option('--hgnc_id',
                default=[]
)
def cli(institute, case, thousand_g, hgnc_id):
    """Test the vcf class."""
    import hashlib
    
    def generate_md5_key(list_of_arguments):
      """Generate an md5-key from a list of arguments"""
      h = hashlib.md5()
      h.update(' '.join(list_of_arguments))
      return h.hexdigest()
    
    
    print('Institute: %s, Case: %s' % (institute, case))
    my_mongo = MongoAdapter(app='hej')
    
    ### FOR DEVELOPMENT ###
    
    case_id = '_'.join([institute, family])
    my_case = my_mongo.case(case_id)
    
    print('Case found:')
    pp(json.loads(my_case.to_json()))
    print('')
    
    
    variant_count = 0
    
    numbers_matched = 0
    for variant in my_mongo.variants(case_id):
      pp(json.loads(variant.to_json()))
      numbers_matched += 1
    print('Number of variants: %s' % (numbers_matched))

if __name__ == '__main__':
    cli()
