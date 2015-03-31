#!/usr/bin/env python
# encoding: utf-8
"""
get_compounds.py

Get the compounds of a variant.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, unicode_literals, print_function,)

import sys
import os

import click

from ....models import Compound
from . import generate_md5_key

def get_compounds(variant, case, variant_type):
  """
  Get a list with mongoengine compounds for this variant.

  Arguments:
    variant       : A Variant dictionary
    rank_score    : The rank score for the variant
    case          : A case object
    variant_type  : 'research' or 'clinical'

  Returns:
    compounds     : A list of mongo engine compound objects
  """

  # We need the case to construct the correct id
  case_id = case.case_id
  case_name = case.display_name

  compounds = []
  for compound in variant['compound_variants'].get(case_name, []):
    compound_name = compound['variant_id']
    # The compound id have to match the document id
    compound_id = generate_md5_key(compound_name.split('_') +
                                   [variant_type] +
                                   case_id.split('_'))
    try:
      compound_score = float(compound['compound_score'])

    except TypeError:
      compound_score = 0.0

    mongo_compound = Compound(variant=compound_id,
                              display_name=compound_name,
                              combined_score=compound_score)

    compounds.append(mongo_compound)

  return compounds

@click.command()
@click.option('-f', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-p', '--ped_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
@click.option('-c', '--scout_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the config file for loading the variants."
)
@click.option('-t', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='cmms',
                nargs=1,
                help="Specify the file format of the ped (or ped like) file."
)
@click.option('--variant_type',
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
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(vcf_file, ped_file, scout_config_file, family_type, variant_type,
        institute, verbose):
  """Test the vcf class."""

  from vcf_parser import VCFParser
  from ....models import Case
  from ..config_parser import ConfigParser
  from . import get_case

  setup_configs = {}

  if scout_config_file:
    setup_configs = ConfigParser(scout_config_file)

  if vcf_file:
    setup_configs['load_vcf'] = vcf_file

  if ped_file:
    setup_configs['ped'] = ped_file

  if institute:
    setup_configs['institutes'] = [institute]

  if not setup_configs.get('load_vcf', None):
    print("Please provide a vcf file.(Use flag '-vcf/--vcf_file')", file=sys.stderr)
    sys.exit(0)

  # Check that the ped file is provided:
  if not setup_configs.get('ped', None):
    print("Please provide a ped file.(Use flag '-ped/--ped_file')", file=sys.stderr)
    sys.exit(0)

  my_case = get_case(setup_configs, family_type)

  vcf_parser = VCFParser(infile=setup_configs['load_vcf'], split_variants=True)
  for variant in vcf_parser:
    compounds = get_compounds(variant, my_case, variant_type)
    for compound in compounds:
      print(compound.to_json())

if __name__ == '__main__':
    cli()
