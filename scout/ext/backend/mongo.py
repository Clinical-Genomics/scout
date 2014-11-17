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


from . import BaseAdapter
from .config_parser import ConfigParser

from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

from pprint import pprint as pp

class MongoAdapter(BaseAdapter):
  """Adapter for cummunication between the scout server and a mongo database."""
  
  # def init_app(self, app, vcf_directory=None, config_file=None):
  def __init__(self,  mongo_db=None, config_file=None):
    # get root path of the Flask app
    # project_root = '/'.join(app.root_path.split('/')[0:-1])
    
    client = MongoClient('localhost', 27017)
    db = client.variantDatabase
    # combine path to the local development fixtures
    project_root = '/vagrant/scout'
    
    self.config_object = ConfigParser(config_file)
    
    self.case_collection = db.cases
    self.variant_collection = db.variants
    
    for case in self.cases():
      pp(case)
      # for development:
      # case_id = case['_id']
      # for variant in self.variants(case_id):
      #   pp(variant)
      # print(case_id)
  
  
  def cases(self):
    for case in self.case_collection.find():
      yield case

  def case(self, case_id):
    
    return self.case_collection.find_one({ '_id' : case_id })
  
  
  def format_variant(self, variant):
    """Return the variant in a format specified for scout."""
    
    formated_variant = variant
    # formated_variant['id'] = variant['variant_id']
    # for category in self.config_object.categories:
    #   for member in self.config_object.categories[category]:
    #     if category != 'config_info':
    #       formated_variant[self.config_object[member]['internal_record_key']] = get_value(variant, category, member)
    
    return formated_variant
  
  
  def variants(self, case_id, query=None, variant_ids=None, nr_of_variants = 10, skip = 0):
  
    # if variant_ids:
    #   return self._many_variants(variant_ids)

    variants = []
    nr_of_variants = skip + nr_of_variants
    print('Searching')
    for variant in self.variant_collection.find()[skip:nr_of_variants]:
      yield variant
      # yield self.format_variant(variant)


  def variant(self, variant_id):
    
    return self.format_variant(self.variant_collection.find_one({ '_id' : variant_id}))

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

@click.command()
# @click.argument('vcf_dir',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
# @click.argument('ped_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
@click.argument('config_file',
                nargs=1,
                type=click.Path(exists=True)
)
# @click.argument('outfile',
#                 nargs=1,
#                 type=click.File('w')
# )
def cli(config_file):
    """Test the vcf class."""
    my_mongo = MongoAdapter(config_file = config_file)
    # my_vcf.init_app('app', vcf_dir, config_file)
    
    # for case in my_vcf.cases():
    #   pp(case)
    # print('')
    
    # for case in my_vcf._cases:
    #   for variant in my_vcf.variants(case['id']):
    #     pp(variant)
    #   print('')

if __name__ == '__main__':
    cli()
