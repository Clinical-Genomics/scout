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

from pymongo import MongoClient, Connection
from mongoengine import connect, DoesNotExist
from mongoengine.connection import _get_db

from scout.ext.backend import load_mongo_db

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(scout.__file__), '..'))

@click.command()
@click.option('-vcf', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-ped', '--ped_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
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
def load_mongo(vcf_file, ped_file, config_file, family_type, mongo_db, username,
        variant_type, madeline, password, institute, port, host, verbose):
  """Test the vcf class."""
  # Check if vcf file exists and that it has the correct naming:
  if not vcf_file:
    print("Please provide a vcf file.(Use flag '-vcf/--vcf_file')", file=sys.stderr)
    sys.exit(0)
  else:
    splitted_vcf_file_name = os.path.splitext(vcf_file)
    vcf_ending = splitted_vcf_file_name[-1]
    if vcf_ending != '.vcf':
      if vcf_ending == '.gz':
        vcf_ending = os.path.splitext(splitted_vcf_file_name)[-1]
        if vcf_ending != '.vcf':
          print("Please use the correct prefix of your vcf file('.vcf/.vcf.gz')", file=sys.stderr)
          sys.ext(0)
      else:
        if vcf_ending != '.vcf':
          print("Please use the correct prefix of your vcf file('.vcf/.vcf.gz')", file=sys.stderr)
          sys.exit(0)
  # Check that the ped file is provided:
  if not ped_file:
    print("Please provide a ped file.(Use flag '-ped/--ped_file')", file=sys.stderr)
    sys.exit(0)
  # Check that the config file is provided:
  if not config_file:
    print("Please provide a config file.(Use flag '-config/--config_file')", file=sys.stderr)
    sys.exit(0)

  my_vcf = load_mongo_db(vcf_file, ped_file, config_file, family_type,
                      mongo_db=mongo_db, username=username, password=password,
                      variant_type=variant_type, madeline_file=madeline, 
                      institute_name=institute, port=port, host=host, 
                      verbose=verbose)


if __name__ == '__main__':
    load_mongo()
