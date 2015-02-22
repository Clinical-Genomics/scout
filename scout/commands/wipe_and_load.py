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

import scout

from pprint import pprint as pp
from pymongo import MongoClient, Connection
from mongoengine import connect, DoesNotExist
from mongoengine.connection import _get_db

from scout.commands.wipe_mongo import wipe_mongo
from scout.commands.load_mongo import load_mongo

from scout.ext.backend import ConfigParser

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(scout.__file__), '..'))

@click.command()
@click.option('-config', '--config_file',
                nargs=1,
                type=click.Path(exists=True),
                default=os.path.join(BASE_PATH, 'configs/config_test.ini'),
                help="Path to the config file for loading the variants. Default configs/config_test.ini"
)
@click.option('-m', '--madeline',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the madeline file with the pedigree."
)
@click.option('-type', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='ped',
                nargs=1,
                help="Specify the file format of the ped (or ped like) file."
)
@click.option('-vt', '--variant_type',
                type=click.Choice(['clinical', 'research']),
                default='clinical',
                nargs=1,
                help="Specify the type of the variants that is being loaded."
)
@click.option('-i', '--institute',
                default='CMMS',
                nargs=1,
                help="Specify the institute that the file belongs to."
)
@click.option('-db', '--mongo-db',
                default='variantDatabase'
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
@click.pass_context
def wipe_and_load(ctx, config_file, madeline, family_type, variant_type, 
                  institute, mongo_db, username, password, port, host,
                  verbose):
  """Drop the mongo database given and rebuild it again."""
  if not mongo_db:
    print("Please specify a database to wipe and populate with flag '-db/--mongo-db'.")
    sys.exit(0)
  
  ctx.invoke(wipe_mongo, 
                  mongo_db=mongo_db, 
                  username=username, 
                  password=password, 
                  port=port, 
                  verbose=verbose
                  )
  
  scout_config_file_1_clinical = os.path.join(
                                BASE_PATH,
                                'tests/vcf_examples/1/scout_config_test_clinical.ini'
                                )
  scout_config_file_1_research = os.path.join(
                                BASE_PATH,
                                'tests/vcf_examples/1/scout_config_test_research.ini'
                                )
  scout_configs_1_clinical = ConfigParser(scout_config_file_1_clinical)
  scout_configs_1_research = ConfigParser(scout_config_file_1_research)
  
  scout_configs_1_clinical['vcf'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_1_clinical['vcf']
                                        )
  scout_configs_1_research['vcf'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_1_research['vcf']
                                        )
  scout_configs_1_clinical['ped'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_1_clinical['ped']
                                        )
  scout_configs_1_research['ped'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_1_research['ped']
                                        )
  scout_configs_1_clinical['madeline'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_1_clinical['madeline']
                                        )
  scout_configs_1_research['madeline'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_1_research['madeline']
                                        )
  
  scout_config_file_coriell_clinical = os.path.join(
                                BASE_PATH,
                                'tests/vcf_examples/P575_coriell/scout_config_test_clinical.ini'
                                )
  scout_config_file_coriell_research = os.path.join(
                                BASE_PATH,
                                'tests/vcf_examples/P575_coriell/scout_config_test_research.ini'
                                )
  
  scout_configs_coriell_clinical = ConfigParser(scout_config_file_coriell_clinical)
  scout_configs_coriell_research = ConfigParser(scout_config_file_coriell_research)
  
  
  scout_configs_coriell_clinical['vcf'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_coriell_clinical['vcf']
                                        )
  scout_configs_coriell_research['vcf'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_coriell_research['vcf']
                                        )
  scout_configs_coriell_clinical['ped'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_coriell_clinical['ped']
                                        )
  scout_configs_coriell_research['ped'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_coriell_research['ped']
                                        )
  scout_configs_coriell_clinical['madeline'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_coriell_clinical['madeline']
                                        )
  scout_configs_coriell_research['madeline'] = os.path.join(
                                          BASE_PATH,
                                          scout_configs_coriell_research['madeline']
                                        )


  # Load the family 1 research data:
  ctx.invoke(load_mongo,
                  vcf_file = scout_configs_1_research['vcf'],
                  ped_file = scout_configs_1_research['ped'],
                  config_file=config_file, 
                  family_type='cmms', 
                  mongo_db=mongo_db, 
                  username=username,
                  variant_type='research', 
                  password=password, 
                  port=port, 
                  host=host, 
                  verbose=verbose
                  )
  # Load the family 1 clinical data:
  ctx.invoke(load_mongo,
                  vcf_file = scout_configs_1_clinical['vcf'],
                  ped_file = scout_configs_1_clinical['ped'],
                  config_file=config_file, 
                  family_type='cmms', 
                  mongo_db=mongo_db, 
                  username=username,
                  variant_type='clinical', 
                  password=password, 
                  port=port, 
                  host=host, 
                  verbose=verbose
                  )
  # Load the family P575-coriell research data:
  ctx.invoke(load_mongo,
                  vcf_file = scout_configs_coriell_research['vcf'],
                  ped_file = scout_configs_coriell_research['ped'],
                  config_file=config_file, 
                  family_type='cmms', 
                  mongo_db=mongo_db, 
                  username=username,
                  variant_type='research', 
                  password=password, 
                  port=port, 
                  host=host, 
                  verbose=verbose
                  )
  # Load the family P575-coriell clinical data:
  ctx.invoke(load_mongo,
                  vcf_file = scout_configs_coriell_research['vcf'],
                  ped_file = scout_configs_coriell_research['ped'],
                  config_file=config_file, 
                  family_type='cmms', 
                  mongo_db=mongo_db, 
                  username=username,
                  variant_type='clinical', 
                  password=password, 
                  port=port, 
                  host=host, 
                  verbose=verbose
                  )
  

if __name__ == '__main__':
    wipe_and_load()
