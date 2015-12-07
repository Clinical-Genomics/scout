#!/usr/bin/env python
# encoding: utf-8
"""
delete_case.py

Script to delete a case and all of its variants from the database.

Created by Måns Magnusson on 2015-04-07.
Copyright (c) 2015 ScoutTeam__. All rights reserved.

"""


from __future__ import (print_function)

import sys
import os
import logging

import click

from pymongo import MongoClient, Connection
from pymongo.errors import CollectionInvalid,PyMongoError
from mongoengine import connect, DoesNotExist
from mongoengine.connection import _get_db

from ..models import (Case, Variant)

def remove_case(case_id, owner, mongo_db='variantDatabase', username=None, 
                password=None, port=27017, host='localhost', logger=None):
  """Delete variants and users from the mongo database."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  if not logger:
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
  
  case_mongo_id = '_'.join([owner, case_id])
  
  databases = connection.database_names()
  logger.info("Databases found: {0}".format(', '.join(databases)))
  if mongo_db in databases:
    logger.info("Accsessing {0}".format(mongo_db))
    db = connection[mongo_db]
    logger.debug("Access succesful")
    
    logger.info("Trying to find case {0} in database".format(case_mongo_id))
    case = Case.objects(case_id=case_mongo_id)
    if case:
      logger.info("Case found! Deleting case")
      case.delete()
      logger.debug("Case deleted")
    else:
      logger.info("Case {0} not found in database".format(case_mongo_id))
    
    nr_of_variants = 0
    for variant in Variant.objects(case_id = case_mongo_id):
      logger.debug("Found variant {0}".format(variant))
      variant.delete()
      logger.debug("Variant deleted")
      nr_of_variants += 1
    
    if nr_of_variants == 0:
      logger.info("No variants that belong to case found in database")
    else:
      logger.info("Deleted {0} variants".format(nr_of_variants))
    
  else:
    raise PyMongoError('{0} database does not exist'.format(mongo_db))
  

@click.command()
@click.option('-c', '--case_id', 
                default=None
)
@click.option('-o', '--owner', 
                default=None
)
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
def delete_case(case_id, owner, mongo_db, username, password, port, host, verbose):
  """
  Delete a case and all of its variants from the mongo database.
  """
  logger = logging.getLogger('scout.commands.delete_case')
  
  logger.info("Running delete_case")
  
  if not mongo_db:
    logger.warning("Please specify a database to wipe and populate"\
                    " with flag '-db/--mongo-db'.")
    sys.exit(0)

  if not case_id:
    logger.warning("Please specify the id of the case that should be deleted"\
                   " with flag '-c/--case_id'.")
    sys.exit(0)

  if not owner:
    logger.warning("Please specify the owner of the case that should be deleted"\
                   " with flag '-o/--owner'.")
    sys.exit(0)
  
  remove_case(case_id, owner, mongo_db, username, password, port, host, logger)
  

if __name__ == '__main__':
  from scout.log import init_log
  logger = logging.getLogger('scout')
  init_log(logger, loglevel='DEBUG')
  delete_case()
