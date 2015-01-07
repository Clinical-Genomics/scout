#!/usr/bin/env python
# encoding: utf-8
"""
load_mongo.py

Load script for the mongo db.
Should take a directory as input, like the load part of vcf.py, and populate the mongo database.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

# Questions for Mats:
# - Should we first check if variant is in database and then update?
# - Is it more effective to, like in sql, update the database with alot of data at the same time or can we do one and one?
# - How to handle general and specific?
# - How to initiate an index on a field?
# - What does this pymongo.ASCENDING means?



from __future__ import absolute_import, unicode_literals, print_function

import sys
import os

import io
import json
import click
import hashlib


from datetime import datetime
from six import string_types
from pymongo import MongoClient
from mongoengine import connect, DoesNotExist


from .config_parser import ConfigParser
from ...models import (Case, Individual, Institute, Variant, GTCall, VariantCommon, 
                        VariantCaseSpecific, Compound, Gene, Transcript)

from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

from pprint import pprint as pp

GENETIC_REGIONS = set(['exonic', 
                        'splicing', 
                        'ncRNA_exonic', 
                        'intronic', 
                        'ncRNA', 
                        'upstream', 
                        'downstream',
                        '5UTR',
                        '3UTR'
                      ]
)

NON_GENETIC_REGIONS = 0

SO_TERMS = {
  'transcript_ablation': {'rank':1, 'region':'exonic'},
  'splice_donor_variant': {'rank':2, 'region':'splicing'},
  'splice_acceptor_variant': {'rank':3, 'region':'splicing'},
  'stop_gained': {'rank':4, 'region':'exonic'},
  'frameshift_variant': {'rank':5, 'region':'exonic'},
  'stop_lost': {'rank':6, 'region':'exonic'},
  'initiator_codon_variant': {'rank':7, 'region':'exonic'},
  'inframe_insertion': {'rank':8, 'region':'exonic'},
  'inframe_deletion': {'rank':9, 'region':'exonic'},
  'missense_variant': {'rank':10, 'region':'exonic'},
  'transcript_amplification': {'rank':11, 'region':'exonic'},
  'splice_region_variant': {'rank':12, 'region':'splicing'},
  'incomplete_terminal_codon_variant': {'rank':13, 'region':'exonic'},
  'synonymous_variant': {'rank':14, 'region':'exonic'},
  'stop_retained_variant': {'rank':15, 'region':'exonic'},
  'coding_sequence_variant': {'rank':17, 'region':'exonic'},
  'mature_miRNA_variant': {'rank':18, 'region':'ncRNA_exonic'},
  '5_prime_UTR_variant': {'rank':19, 'region':'5UTR'},
  '3_prime_UTR_variant': {'rank':20, 'region':'3UTR'},
  'non_coding_transcript_exon_variant': {'rank':21, 'region':'ncRNA_exonic'},
  'non_coding_exon_variant': {'rank':21, 'region':'ncRNA_exonic'},
  'non_coding_transcript_variant': {'rank':22, 'region':'ncRNA_exonic'},
  'nc_transcript_variant': {'rank':22, 'region':'ncRNA_exonic'},
  'intron_variant': {'rank':23, 'region':'intronic'},
  'NMD_transcript_variant': {'rank':24, 'region':'ncRNA'},
  'upstream_gene_variant': {'rank':25, 'region':'upstream'},
  'downstream_gene_variant': {'rank':26, 'region':'downstream'},
  'TFBS_ablation': {'rank':27, 'region':'TFBS'},
  'TFBS_amplification': {'rank':28, 'region':'TFBS'},
  'TF_binding_site_variant': {'rank':29, 'region':'TFBS'},
  'regulatory_region_ablation': {'rank':30, 'region':'regulatory_region'},
  'regulatory_region_amplification': {'rank':31, 'region':'regulatory_region'},
  'regulatory_region_variant': {'rank':33, 'region':'regulatory_region'},
  'feature_elongation': {'rank':34, 'region':'genomic_feature'},
  'feature_truncation': {'rank':35, 'region':'genomic_feature'},
  'intergenic_variant': {'rank':36, 'region':'intergenic_variant'}
}

def load_mongo(vcf_file=None, ped_file=None, config_file=None,
               family_type='ped', mongo_db='variantDatabase', institute_name='CMMS',
               username=None, password=None, verbose = False):
  """Populate a moongo database with information from ped and variant files."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])

  connect(mongo_db, host='localhost', port=27017, username=username,
          password=password)
  
  if verbose:
    print("\nvcf_file:\t%s\nped_file:\t%s\nconfig_file:\t%s\nfamily_type:\t%s\nmongo_db:\t%s\ninstitute:\t%s\n" % 
              (vcf_file, ped_file, config_file, family_type, mongo_db, institute_name), file=sys.stderr)
  
  ######## Parse the config file to check for keys: ########
  config_object = ConfigParser(config_file)
  
  ######## Add the institute to the mongo db: ########
  
  institute = get_institute(institute_name)
  try:
    if Institute.objects.get(internal_id = institute.internal_id):
      institute = Institute.objects.get(internal_id = institute.internal_id)
  except DoesNotExist:
    if verbose:
      print('New institute!', file=sys.stderr)
    
  
  ######## Get the case and add it to the mongo db: ########
  individuals = []
  cases = get_case(ped_file, family_type, institute_name)
  for case in cases:
    if case not in institute.cases:
      institute.cases.append(case)
    for individual in case.individuals:
      individuals.append(individual.individual_id)
    case.save()
  
  institute.save()
  
  ######## Get the variants and add them to the mongo db: ########
  
  variant_parser = vcf_parser.VCFParser(infile = vcf_file, split_variants = True)
  nr_of_variants = 0
  # for variant in variant_parser:
  #   for info in variant['info_dict']:
  #     print(info)
  #     print(variant['info_dict'][info])
  #   print('')
  #   pp(variant['vep_info'])
  # sys.exit()
  
  start_inserting_variants = datetime.now()
  
  if verbose:
    print('Start parsing variants...', file=sys.stderr)
  
  for variant in variant_parser:
    nr_of_variants += 1
    add_mongo_variant(variant, individuals, case['case_id'], config_object, nr_of_variants)
    if verbose:
      if nr_of_variants % 1000 == 0:
        print('%s variants parsed!' % nr_of_variants, file=sys.stderr)
  
  if verbose:
    print('Variants in non genetic regions: %s' % NON_GENETIC_REGIONS, file=sys.stderr)
    print('%s variants inserted!' % nr_of_variants, file=sys.stderr)
    print('Time to insert variants: %s' % (datetime.now() - start_inserting_variants), file=sys.stderr)

def generate_md5_key(list_of_arguments):
  """
  Generate an md5-key from a list of arguments.
  
  Args:
    list_of_arguments: A list of strings
  
  Returns:
    A md5-key object generated from the list of strings.
  """
  for arg in list_of_arguments:
    if not isinstance(arg, string_types):
      print('Error in generate_md5_key:\n' 'One of the objects in the list of arguments is not a string', file=sys.stderr)
      print('Argument: %s is a %s' % (arg, type(arg)))
      sys.exit(1)
  h = hashlib.md5()
  h.update(' '.join(list_of_arguments))
  return h.hexdigest()


def get_institute(institute_name):
  """
  Take a institute name and return a institute object.
  
  Args:
    institute_name: A string that represents the name of an institute
  
  Returns:
    A mongoengine Institute object described in scout.models.institute.py
  """
  return Institute(internal_id=institute_name, display_name=institute_name)

def get_case(ped_file, family_type, institute_name):
  """Take a case file and return the case on the specified format."""

  case_parser = ped_parser.FamilyParser(ped_file, family_type=family_type)
  cases = []
  for case in case_parser.get_json():
  
    mongo_case = Case(case_id = generate_md5_key([institute_name, case['family_id']]))
    mongo_case['display_name'] = case['family_id']
    individuals = []
    databases = set()
    for individual in case['individuals']:
      ind = Individual()
      ind['father'] = individual['father']
      ind['mother'] = individual['mother']
      ind['display_name'] = individual['individual_id']
      ind['sex'] = str(individual['sex'])
      ind['phenotype'] = individual['phenotype']
      ind['individual_id'] = individual['individual_id']
      ind['capture_kit'] = individual.get('extra_info', {}).get('Capture_kit', '').split(',')
      for clinical_db in individual.get('extra_info', {}).get('Clinical_db', '').split(','):
        databases.add(clinical_db)
      individuals.append(ind)
    mongo_case['individuals'] = individuals
    mongo_case['databases'] = list(databases)
    cases.append(mongo_case)
    
  return cases



def add_mongo_variant(variant, individuals, case_id, config_object, variant_count):
  """Return the variant in a format specified for scout. The structure is decided by the config file that is used."""
  
  def get_genotype_information(variant, genotype_collection, individual):
    """Get the genotype information in the proper format and return ODM specified gt call."""
    mongo_gt_call = GTCall(sample=individual)
    for genotype_information in genotype_collection:
      if config_object[genotype_information]['vcf_format_key'] == 'GT':
        mongo_gt_call['genotype_call'] = variant['genotypes'][individual].genotype
      elif config_object[genotype_information]['vcf_format_key'] == 'DP':
        mongo_gt_call['read_depth'] = variant['genotypes'][individual].depth_of_coverage
      elif config_object[genotype_information]['vcf_format_key'] == 'AD':
        mongo_gt_call['allele_depths'] = [variant['genotypes'][individual].ref_depth,
                                          variant['genotypes'][individual].alt_depth]
      elif config_object[genotype_information]['vcf_format_key'] == 'GQ':
        mongo_gt_call['genotype_quality'] = variant['genotypes'][individual].genotype_quality
    
    return mongo_gt_call
  
  def get_transcript_information(variant):
    """Get the transcript information in the mongoengine format."""
    genes = {}
    best_rank = None
    # vep_info is a list of dictionarys with vep entrys
    # Each vep entry represents a transcript so one transcript belongs to one gene
    for vep_entry in variant['vep_info'].get(variant['ALT'], []):
      # We should first check if the variant is in a genetic region
      # If it is not we do not add any entry
      genetic_region = True
      functional_annotations = vep_entry.get('Consequence', '').split('&')
      for consequence in functional_annotations:
        if consequence in GENETIC_REGIONS:
          genetic_region = False
    
      if genetic_region:
        transcript_id = vep_entry.get('Feature', '').split(':')[0]
        transcript = Transcript(transcript_id = transcript_id)
        if vep_entry.get('PolyPhen', None):
          transcript.polyphen = vep_entry['PolyPhen']
        if vep_entry.get('SIFT', None):
          transcript.sift = vep_entry['SIFT']
        if vep_entry.get('EXON', None):
          transcript.exon = vep_entry['EXON']
        if vep_entry.get('INTRON', None):
          transcript.intron = vep_entry['INTRON']
      
        hgnc_id = vep_entry.get('SYMBOL', '').split('.')[0]
      
        if hgnc_id not in genes:
          # We need to store information of the most severe transcript
          genes[hgnc_id] = {'most_severe_transcript': None,
                              'transcripts': {}
                            }
          best_rank = None
    
        coding_sequence_entry = vep_entry.get('HGVSc', '').split(':')
        protein_sequence_entry = vep_entry.get('HGVSp', '').split(':')
    
        # If there is a coding sequence entry we need to parse it:
        coding_sequence_name = None
        if len(coding_sequence_entry) > 1:
          # print('Coding sequence: %s' % coding_sequence_entry)
          coding_sequence_name = coding_sequence_entry[-1].split('.')[1]          
      
        if coding_sequence_name:
          transcript.coding_sequence_name = coding_sequence_name
      
        # If there is a protein sequence entry we need to parse it:
        protein_sequence_name = None
        if len(protein_sequence_entry) > 1:
          # print('Protein sequence: %s' % protein_sequence_entry)
          protein_sequence_name = protein_sequence_entry[-1].split('.')[1]
        
        if protein_sequence_name:
          transcript.protein_sequence_name = protein_sequence_name
        
        functional_annotation = None
        region_annotation = None
        for functional_annotation in functional_annotations:
          if functional_annotation:
            # Get the rank for this type of genetic feature:
            rank = SO_TERMS[functional_annotation]['rank']
            region_annotation = SO_TERMS[functional_annotation]['region']
            if best_rank:
              # If this is the 'worst' feature annotaded we will show it
              if rank < best_rank:
                genes[hgnc_id]['most_severe_transcript'] = transcript_id
                transcript.functional_annotation = functional_annotation
                transcript.region_annotation = region_annotation
                best_rank = rank
            else:
              genes[hgnc_id]['most_severe_transcript'] = transcript_id
              transcript.functional_annotation = functional_annotation
              transcript.region_annotation = region_annotation
              best_rank = rank
        
        genes[hgnc_id]['transcripts'][transcript_id] = transcript
      
      else:
        NON_GENETIC_REGIONS += 1
    
    mongo_genes = {}
    for gene in genes:
      most_severe = genes[gene]['most_severe_transcript']
      transcripts = []
      mongo_gene = Gene(hgnc_symbol=gene)
      for transcript in genes[gene]['transcripts']:
        transcripts.append(genes[gene]['transcripts'][transcript])
      mongo_gene.transcripts = transcripts
      try:
        mongo_gene.functional_annotation = genes[gene]['transcripts'][most_severe].functional_annotation
      except AttributeError:
        pass
      try:
        mongo_gene.region_annotation = genes[gene]['transcripts'][most_severe].region_annotation
      except AttributeError:
        pass
      try:
        mongo_gene.sift_prediction = genes[gene]['transcripts'][most_severe].sift
      except AttributeError:
        pass
      try:
        mongo_gene.polyphen_prediction = genes[gene]['transcripts'][most_severe].polyphen
      except AttributeError:
        pass
      # Add the mongo engine gene to the dictionary
      mongo_genes[gene] = mongo_gene
    
    return mongo_genes
  
  
  id_fields = [variant['CHROM'], variant['POS'], variant['REF'], variant['ALT']]
  variant_id = generate_md5_key(id_fields)
 
  # We first add the case specific information
  # Add the information that is specific to this case
  mongo_specific = VariantCaseSpecific(case_id = case_id)
  try:
    mongo_specific['rank_score'] = float(variant['info_dict'][config_object['RankScore']['vcf_info_key']][0])
  except KeyError:
    mongo_specific['rank_score'] = 0.0
  
  mongo_specific['variant_rank'] = variant_count
  mongo_specific['quality'] = float(variant['QUAL'])
  mongo_specific['filters'] = variant['FILTER'].split(';')

  # Add the compound information:
  compounds = []
  for compound in variant['info_dict'].get(config_object['Compounds']['vcf_info_key'], []):
    try:
      splitted_compound = compound.split('>')
      compound_name = splitted_compound[0]
      compound_individual_score = float(splitted_compound[1])
      mongo_compound = Compound(variant_id=generate_md5_key(compound_name.split('_')),
                              display_name = compound_name,
                              rank_score = compound_individual_score,
                              combined_score = mongo_specific['rank_score'] + compound_individual_score
                              )
      compounds.append(mongo_compound)
    except IndexError:
      pass
  
  mongo_specific['compounds'] = compounds
  
  # Add the inheritance patterns:
  
  models = variant['info_dict'].get(config_object['GeneticModels']['vcf_info_key'], None)
  if models:
    genetic_models = []
    for family_models in models:
      for model in family_models.split(':')[-1].split('|'):
        genetic_models.append(model)
      mongo_specific['genetic_models'] = genetic_models

  # Add the gt calls:

  gt_calls = []
  for individual in individuals:
    # This function returns an ODM GTCall object with the relevant information:
    gt_calls.append(get_genotype_information(variant, config_object.categories['genotype_information'], individual))

  mongo_specific['samples'] = gt_calls

  # Variant.objects(variant_id=variant_id).update_one(push__specific=mongo_specific)

  # If the variant exists we only need to update the relevant information:
  try:

    if Variant.objects.get(variant_id = variant_id):
      Variant.objects(variant_id = variant_id).update(**{('set__specific__%s' % case_id) : mongo_specific})

  except DoesNotExist:
    # We insert the family with the md5-key as id, same key we use in cases
    # Add the core information about the variant
    mongo_variant = Variant(variant_id = variant_id,
                            display_name = '_'.join(id_fields),
                            chromosome = variant['CHROM'],
                            position = int(variant['POS']),
                            reference = variant['REF'],
                            alternative = variant['ALT']
                    )

    mongo_variant['db_snp_ids'] = variant['ID'].split(';')

    mongo_common = VariantCommon()
    # Add the gene info
    
    mongo_common['genes'] = get_transcript_information(variant)
    
    mongo_common['ensemble_gene_ids'] = variant['info_dict'].get(config_object['Ensembl_gene_id']['vcf_info_key'], [])
    # Add the frequencies
    try:
      mongo_common['thousand_genomes_frequency'] = float(
                                            variant['info_dict'].get(config_object['1000GMAF']['vcf_info_key'], ['0'])[0]
                                            )
    except ValueError:
      pass
    
    try:
      mongo_common['exac_frequency'] = float(variant['info_dict'].get(config_object['EXAC']['vcf_info_key'], ['0'])[0])
    except ValueError:
      pass
    
    # Add the severity predictions
    mongo_common['cadd_score'] = float(variant['info_dict'].get(config_object['CADD']['vcf_info_key'], ['0'])[0])
    
    # Add conservation annotation
    mongo_common['gerp_conservation'] = variant['info_dict'].get(config_object['Gerp']['vcf_info_key'], [])
    
    mongo_common['phast_conservation'] = variant['info_dict'].get(config_object['PhastCons']['vcf_info_key'], [])
    
    mongo_common['phylop_conservation'] = variant['info_dict'].get(config_object['PhylopCons']['vcf_info_key'], [])
    
    # Add the common field:
    mongo_variant['common'] = mongo_common
    
    # When we save the variant in this stage it will be an upsert when using mongoengine
    mongo_variant['specific'][case_id] = mongo_specific
    # print('JSON')
    # print(mongo_variant.to_json())
    # print()
    mongo_variant.save()
  
  return


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
@click.option('-config', 'config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the config file for loading the variants."
)
@click.option('-type', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                nargs=1,
                help="Specify the file format of the ped (or ped like) file."
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
@click.option('-v', '--verbose', 
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(vcf_file, ped_file, config_file, family_type, mongo_db, username,
        password, verbose):
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
          sys.ext(0)
  # Check that the ped file is provided:
  if not ped_file:
    print("Please provide a ped file.(Use flag '-ped/--ped_file')", file=sys.stderr)
    sys.exit(0)
  # Check that the config file is provided:
  if not config_file:
    print("Please provide a config file.(Use flag '-config/--config_file')", file=sys.stderr)
    sys.exit(0)
  
  my_vcf = load_mongo(vcf_file, ped_file, config_file, family_type,
                      mongo_db=mongo_db, username=username, password=password, verbose=verbose)


if __name__ == '__main__':
    cli()
