#!/usr/bin/env python
# encoding: utf-8
"""
get_mongo_variant.py

Create a mongo engine variant object from a variant dictionary.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, unicode_literals, print_function,)

import sys
import os
import click

from ....models import (Variant)

from . import (get_genes, get_genotype, get_compounds, generate_md5_key)

from pprint import pprint as pp

# These are the valid SO terms with corresponfing severity rank
def get_mongo_variant(variant, variant_type, individuals, case, config_object, variant_count):
  """
  Take a variant and some additional information, convert it to mongo engine
  objects and put them in the proper format in the database.

  Input:
    variant       : A Variant dictionary
    variant_type  : A string in ['clinical', 'research']
    individuals   : A list with the id:s of the individuals
    case_id       : The md5 string that represents the ID for the case
    variant_count : The rank order of the variant in this case
    config_object : A config object with the information from the config file

  Returns:
    mongo_variant : A variant parser into the proper mongo engine format.

  """

  #############################################################################################################
  #### Here is the start for parsing the variants                                                          ####
  #############################################################################################################
  # Create the ID for the variant
  case_id = case.case_id
  case_name = case.display_name

  id_fields = [
                variant['CHROM'],
                variant['POS'],
                variant['REF'],
                variant['ALT'],
                variant_type
              ]

  variant_id = generate_md5_key(id_fields)
  document_id = generate_md5_key(id_fields+case_id.split('_'))

  # Create the mongo variant object
  mongo_variant = Variant(
                          document_id = document_id,
                          variant_id = variant_id,
                          variant_type = variant_type,
                          case_id = case_id,
                          display_name = '_'.join(id_fields),
                          chromosome = variant['CHROM'],
                          position = int(variant['POS']),
                          reference = variant['REF'],
                          alternative = variant['ALT'],
                          variant_rank = variant_count,
                          quality = float(variant['QUAL']),
                          filters = variant['FILTER'].split(';')
                  )

  # If a variant belongs to any gene lists we check which ones
  mongo_variant['gene_lists'] = variant['info_dict'].get(
          config_object['VCF']['GeneLists']['vcf_info_key'],
          None
          )

  ################# Add the rank score and variant rank #################
  # Get the rank score as specified in the config file.
  # This is central for displaying variants in scout.

  mongo_variant['rank_score'] = float(
      variant.get('rank_scores', {}).get(case_name, 0.0)
    )

  ################# Add gt calls #################
  gt_calls = []
  for individual in individuals:
    # This function returns an ODM GTCall object with the
    # relevant information for a individual:
    gt_calls.append(get_genotype(
                                  variant,
                                  config_object,
                                  individual
                                )
                            )
  mongo_variant['samples'] = gt_calls

  ################# Add the compound information #################

  mongo_variant['compounds'] = get_compounds(
                                          variant,
                                          case,
                                          variant_type
                                        )

  ################# Add the inheritance patterns #################

  mongo_variant['genetic_models'] = variant.get(
                                        'genetic_models',
                                        {}
                                        ).get(
                                            case_name,
                                            []
                                            )

  ################# Add the gene and tanscript information #################

  # Get genes return a list with ODM objects for each gene
  mongo_variant['genes'] = get_genes(variant)
  hgnc_symbols = set([])
  ensembl_gene_ids = set([])

  # Add the clinsig prediction
  clnsig = variant.get('CLNSIG', None)
  if clnsig:
    try:
      mongo_variant['clnsig'] = int(clnsig[0])
    except (ValueError, IndexError):
      pass

  for gene in mongo_variant.genes:
    hgnc_symbols.add(gene.hgnc_symbol)
    ensembl_gene_ids.add(gene.ensembl_gene_id)

  mongo_variant['hgnc_symbols'] = list(hgnc_symbols)

  mongo_variant['ensembl_gene_ids'] = list(ensembl_gene_ids)

  ################# Add a list with the dbsnp ids #################

  mongo_variant['db_snp_ids'] = variant['ID'].split(';')

  ################# Add the frequencies #################

  try:
    mongo_variant['thousand_genomes_frequency'] = float(
                                variant['info_dict'].get(
                                  config_object['VCF']['1000GMAF']['vcf_info_key'],
                                  ['0'])[0]
                                )
  except ValueError:
    pass

  try:
    mongo_variant['exac_frequency'] = float(
                                variant['info_dict'].get(
                                  config_object['VCF']['EXAC']['vcf_info_key'],
                                  ['0'])[0]
                                )
  except ValueError:
    pass

  # Add the severity predictions
  mongo_variant['cadd_score'] = float(
                          variant['info_dict'].get(
                            config_object['VCF']['CADD']['vcf_info_key'],
                            ['0'])[0]
                          )
  # Add conservation annotation
  mongo_variant['gerp_conservation'] = variant['info_dict'].get(
                                  config_object['VCF']['Gerp']['vcf_info_key'],
                                  []
                                )
  mongo_variant['phast_conservation'] = variant['info_dict'].get(
                                  config_object['VCF']['PhastCons']['vcf_info_key'],
                                  []
                                )
  mongo_variant['phylop_conservation'] = variant['info_dict'].get(
                                  config_object['VCF']['PhylopCons']['vcf_info_key'],
                                  []
                                )

  return mongo_variant


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
@click.option('--vcf_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the config file for loading the variants."
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
def cli(vcf_file, ped_file, vcf_config_file, scout_config_file, family_type,
        variant_type, institute, verbose):
  """
  Test generate mongo variants.
  """

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

  # Check that the config file is provided:
  if not vcf_config_file:
    print("Please provide a config file.(Use flag '-vcf_config/--vcf_config_file')", file=sys.stderr)
    sys.exit(0)

  config_object = ConfigParser(vcf_config_file)

  my_case = get_case(setup_configs, family_type)

  vcf_parser = VCFParser(infile=setup_configs['load_vcf'], split_variants=True)

  individuals = vcf_parser.individuals

  variant_count = 0
  for variant in vcf_parser:
    variant_count += 1
    mongo_variant = get_mongo_variant(
                        variant,
                        variant_type,
                        individuals,
                        my_case,
                        config_object,
                        variant_count
                      )
    print(mongo_variant.to_json())


if __name__ == '__main__':
    cli()
