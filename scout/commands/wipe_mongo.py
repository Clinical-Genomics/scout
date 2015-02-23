#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""


from __future__ import absolute_import, unicode_literals, print_function

import sys
import os

import click

from pymongo import MongoClient, Connection
from mongoengine import connect, DoesNotExist
from mongoengine.connection import _get_db


def drop_mongo(mongo_db='variantDatabase', username=None, password=None, 
              port=27017, host='localhost', verbose=False):
  """Delete variants and users from the mongo database."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  
  if verbose:
    print('Trying to access collection %s' % mongo_db, file=sys.stderr)
  
  connection = connect(
                    mongo_db, 
                    host=host, 
                    port=port, 
                    username=username,
                    password=password
                    )
  
  collections = connection.database_names()
  if mongo_db in collections:  
    db = connection[mongo_db]
    # Drop the case collection:
    case_collection = db['case']
    if verbose:
      print("Dropping collection 'case' ...")
    case_collection.drop()
    # Drop the institute collection:
    institute_collection = db['institute']
    if verbose:
      print("Dropping collection 'institute' ...")
    institute_collection.drop()
    if verbose:
      print("Cases dropped.")
    # Drop the variant collection:    
    variant_collection = db['variant']
    if verbose:
      print("Dropping collection 'variant...")
    variant_collection.drop()
    if verbose:
      print("Variants dropped.")
  else:
    print('%s does not exist in database.' % mongo_db)
    print('Existing connections: %s' % connection.database_names())
  

# def load_mongo(connection, mongo_db):
#   """Populate the mongodatabase with test data"""
#   pass

@click.command()
@click.option('-db', '--mongo-db', 
                default=None
)
@click.option('-u', '--username', 
                type=str
)
@click.option('-p', '--password', 
                type=str
)
@click.option('-port', '--port',
                default=27017,
                help='Specify the port where to look for the mongo database.'
)
@click.option('-h', '--host',
                default='localhost',
                help='Specify the host where to look for the mongo database.'
)
@click.option('-v', '--verbose', 
                is_flag=True,
                help='Increase output verbosity.'
)
def wipe_mongo(mongo_db, username, password, port, host, verbose):
  """Drop the mongo database given and rebuild it again."""
  if not mongo_db:
    print("Please specify a database to wipe and populate with flag '-db/--mongo-db'.")
    sys.exit(0)
  else:
    drop_mongo(mongo_db, username, password, port, host, verbose)
  

if __name__ == '__main__':
    wipe_mongo()
