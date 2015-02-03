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

from ..scout.ext.backend import load_mongo


def drop_mongo(connection, mongo_db):
  """Delete the mongo database."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  collections = connection.database_names()
  if mongo_db in collections:  
    db = connection[mongo_db]
    # Drop the case collection:
    case_collection = db['case']
    print("Dropping collection 'case' ...")
    case_collection.drop()
    print("Cases dropped.")
    # Drop the variant collection:    
    variant_collection = db['variant']
    print("Dropping collection 'variant...")
    variant_collection.drop()
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
@click.option('-v', '--verbose', 
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(mongo_db, username, password, verbose):
  """Drop the mongo database given and rebuild it again."""
  if not mongo_db:
    print("Please specify a database to wipe and populate with flag '-db/--mongo-db'.")
    sys.exit(0)
  else:
    print('Trying to access collection %s' % mongo_db, file=sys.stderr)
    connection = Connection('localhost', 27017) # Connect to the database
    drop_mongo(connection, mongo_db)
    # load_mongo(connection, mongo_db)
  

if __name__ == '__main__':
    cli()
