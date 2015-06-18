#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""


from __future__ import (absolute_import, unicode_literals, print_function)

import sys
import os
import logging

import click

from pymongo import MongoClient, Connection
from mongoengine import connect, DoesNotExist
from mongoengine.connection import _get_db


def drop_mongo(mongo_db='variantDatabase', username=None, password=None, 
              port=27017, host='localhost'):
  """Delete variants and users from the mongo database."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  
  logger = logging.getLogger(__name__)
  
  logger.info('Trying to access collection {0}'.format(mongo_db))

  connection = connect(
                    mongo_db, 
                    host=host, 
                    port=port, 
                    username=username,
                    password=password
                    )

  logger.debug('Connection successful')
  
  # We assume that the collection exists
  db = connection[mongo_db]
  # Drop the case collection:
  case_collection = db['case']
  logger.info("Dropping collection 'case'")
  case_collection.drop()
  logger.debug("Case collection dropped")
  # Drop the institute collection:
  institute_collection = db['institute']
  logger.info("Dropping collection 'institute'")
  institute_collection.drop()
  logger.debug("Institute collection dropped")
  # Drop the variant collection:    
  logger.info("Dropping collection 'variant'")
  variant_collection = db['variant']
  variant_collection.drop()
  logger.debug("Variants dropped.")
  

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
def wipe(mongo_db, username, password, port, host, verbose):
  """Drop the mongo database given and rebuild it again."""
  logger = logging.getLogger(__name__)
  
  logger.info("Running wipe_mongo")
  
  if not mongo_db:
    logger.warning("Please specify a database to wipe and populate with flag '-db/--mongo-db'.")
    sys.exit(0)
  else:
    drop_mongo(mongo_db, username, password, port, host)
  

if __name__ == '__main__':
  from ..log import init_log
  logger = logging.getLogger(__name__)
  init_log(logger, loglevel="DEBUG")
  wipe()
