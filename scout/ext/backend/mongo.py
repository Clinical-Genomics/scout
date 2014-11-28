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
from mongoengine import connect
from mongoengine.errors import DoesNotExist

from . import BaseAdapter
from .config_parser import ConfigParser
from ...models import *


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

    connect(database, host=host, port=port)


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
      return Case.objects.get(pk = case_id)
    except DoesNotExist:
      return None

  def variants(self, case_id, query=None, variant_ids=None, nr_of_variants = 10, skip = 0):

    variants = []
    nr_of_variants = skip + nr_of_variants
    case_specific = ('specific.%s' % case_id)
    return Variant.objects(__raw__ = {case_specific: {'$exists' : True}}).order_by(
                                      case_specific + '.variant_rank')[skip:nr_of_variants]

  def variant(self, variant_id):

    try:
      return Variant.objects.get(pk = variant_id)
    except DoesNotExist:
      return None

  def next_variant(self, variant_id, case_id):
    """Returns the next variant from the rank order"""
    case_specific = ('specific.%s' % case_id)
    previous_variant = Variant.objects.get(pk=variant_id)
    rank = previous_variant['specific'].get(case_id, {}).variant_rank or 0

    try:
      return Variant.objects.get(__raw__ = {case_specific + '.variant_rank': rank+1})
    except DoesNotExist:
      return None

  def previous_variant(self, variant_id, case_id):
    """Returns the next variant from the rank order"""
    case_specific = ('specific.%s' % case_id)
    previous_variant = Variant.objects.get(pk=variant_id)
    rank = previous_variant['specific'].get(case_id, {}).variant_rank or 0

    try:
      return Variant.objects.get(__raw__ = {case_specific + '.variant_rank': rank-1})
    except DoesNotExist:
      return None

@click.command()
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
    # small_family_id = generate_md5_key(['3'])
    # big_family_id = generate_md5_key(['2'])
    case_id = "d7d48f6ffb8d15ed533ad25808d5453b"
    my_case = my_mongo.case(case_id)
    # my_case = my_mongo.case('hej')
    variant_count = 0
    if my_case:
      print(my_case.to_json())
      print('id: %s' % my_case.id)
      for variant in my_mongo.variants(my_case.id, nr_of_variants = 5):
        pp(variant.to_json())
        print('')
        variant_count += 1
    print('Number of variants: %s' % variant_count)
    # for case in my_mongo.cases():
    #   variant_count = 0
    #   pp(case.to_json())
    #   for variant in my_mongo.variants(case.id], nr_of_variants = 20):
    #     pp(variant.to_json)
    #     variant_count += 1
      #   print(variant_count)
    # my_vcf.init_app('app', vcf_dir, config_file)
    # rank = my_mongo.next_variant('0ab656e8fe4aaf8f87405a0bc3b18eba', 'a684eceee76fc522773286a895bc8436')
    # pp(my_mongo.next_variant('0ab656e8fe4aaf8f87405a0bc3b18eba', 'a684eceee76fc522773286a895bc8436'))
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
