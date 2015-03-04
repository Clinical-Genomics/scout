#!/usr/bin/env python
# encoding: utf-8
"""
get_genotype.py

Parse all genotype information and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, unicode_literals, print_function,)

import sys
import os

import click

from pprint import pprint as pp

from ....models import GTCall


def get_genotype(variant, config_object, individual):
  """
  Get the genotype information in the proper format and return ODM specified gt call.

  Args:
    variant : A dictionary with the information about a variant
    genotype_collection : A list with the relevant genotype information for
                          each individual in the vcf file
    individual: A string that represents the individual id

  Returns:
    mongo_gt_call : A mongo engine object with the gt-call information

  """
  genotype_collection = config_object.categories['genotype_information']
  # Initiate a mongo engine gt call object
  mongo_gt_call = GTCall(sample=individual)
  # Fill the onbject with the relevant information:
  for genotype_information in genotype_collection:
    if config_object['VCF'][genotype_information]['vcf_format_key'] == 'GT':
      mongo_gt_call['genotype_call'] = variant['genotypes'][individual].genotype
    
    elif config_object['VCF'][genotype_information]['vcf_format_key'] == 'DP':
      mongo_gt_call['read_depth'] = variant['genotypes'][individual].depth_of_coverage
    
    elif config_object['VCF'][genotype_information]['vcf_format_key'] == 'AD':
      mongo_gt_call['allele_depths'] = [variant['genotypes'][individual].ref_depth,
                                        variant['genotypes'][individual].alt_depth]
    
    elif config_object['VCF'][genotype_information]['vcf_format_key'] == 'GQ':
      mongo_gt_call['genotype_quality'] = variant['genotypes'][individual].genotype_quality
  
  return mongo_gt_call

@click.command()
@click.option('-f', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-c', '--vcf_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the config file for loading the variants."
)
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(vcf_file, vcf_config_file, verbose):
  """
  Test the get_genotype class."""
  from vcf_parser import VCFParser
  from ..config_parser import ConfigParser
  
  if not vcf_config_file:
    print('Please provide a vcf config file')
    sys.exit()
  
  if not vcf_file:
    print('Please provide a vcf file')
    sys.exit()
  
  configs = ConfigParser(vcf_config_file)
  
  vcf_parser = VCFParser(infile=vcf_file, split_variants=True)
  individuals = vcf_parser.individuals
  
  
  for variant in vcf_parser:
    for individual in individuals:
      genotype_info = get_genotype_information(variant, configs, individual)
      print(genotype_info.to_json())

if __name__ == '__main__':
    cli()
