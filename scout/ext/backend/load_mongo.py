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



from __future__ import (absolute_import, unicode_literals, print_function, 
                        division)

import sys
import os

import io
import json
import click
import hashlib


from datetime import datetime
from six import string_types
from pymongo import (ASCENDING, DESCENDING)
from mongoengine import connect, DoesNotExist
from mongoengine.connection import get_db


from .config_parser import ConfigParser
from ...models import (Case, Individual, Institute, Variant, GTCall,
                          Compound, Gene, Transcript)

from vcf_parser import parser as vcf_parser
from ped_parser import FamilyParser

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

# These are the valid region annotations
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

# These are the valid SO terms with corresponfing severity rank
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

def load_mongo_db(vcf_file=None, ped_file=None, config_file=None, 
               family_type='ped', mongo_db='variantDatabase', institute_name='CMMS',
               variant_type='clinical', madeline_file=None, username=None, 
               password=None, port=27017, host='localhost',verbose = False):
  """Populate a moongo database with information from ped and variant files."""
  # get root path of the Flask app
  # project_root = '/'.join(app.root_path.split('/')[0:-1])
  
  connect(mongo_db, host=host, port=port, username=username,
          password=password)
  
  variant_database = get_db()
  
  
  if verbose:
    print("\nvcf_file:\t%s\nped_file:\t%s\nconfig_file:\t%s\nfamily_type:\t%s\nmongo_db:\t%s\ninstitute:\t%s\n" %
              (vcf_file, ped_file, config_file, family_type, mongo_db, institute_name), file=sys.stderr)
  
  
  ######## Parse the config file to check for keys ########
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
  if verbose:
    print('Cases found in %s' % ped_file, file=sys.stderr)
  ped_individuals = []
  cases = get_case(ped_file, family_type, institute_name)
  for case in cases:
    case_id = case.case_id
    case_name = case.display_name
    
    if verbose:
      print('case id %s' % case_name, file=sys.stderr)
    
    # Add the case to its institute
    if case not in institute.cases:
      institute.cases.append(case)
    # Add the individuals of a case
    for individual in case.individuals:
      ped_individuals.append(individual.individual_id)
    # Add the pedigree picture
    if madeline_file:
      with open(madeline_file, 'r') as f:
        case.madeline_info = f.read()
    
  institute.save()
  
  ######## Get the variants and add them to the mongo db: ########
  
  variant_parser = vcf_parser.VCFParser(infile = vcf_file, split_variants = True)
  nr_of_variants = 0
  start_inserting_variants = datetime.now()
  
  # Check which individuals that exists in the vcf file:
  individuals = []
  for individual in ped_individuals:
    if individual in variant_parser.individuals:
      individuals.append(individual)
  
  gene_lists = set([])
  
  if verbose:
    print('Start parsing variants...', file=sys.stderr)
  
  for variant in variant_parser:
    nr_of_variants += 1
    mongo_variant = get_mongo_variant(variant, variant_type, individuals, case, config_object, nr_of_variants)
    for gene_list in mongo_variant['gene_lists']:
      gene_lists.add(gene_list)
    
    mongo_variant.save()
    if verbose:
      if nr_of_variants % 1000 == 0:
        print('%s variants parsed!' % nr_of_variants, file=sys.stderr)
  
  if verbose:
    print('Variants in non genetic regions: %s' % NON_GENETIC_REGIONS, file=sys.stderr)
    print('%s variants inserted!' % nr_of_variants, file=sys.stderr)
    print('Time to insert variants: %s' % (datetime.now() - start_inserting_variants), file=sys.stderr)
  
  
  case.gene_lists = list(set(case.gene_lists).union(gene_lists))
  
  case.save()
  
  
  if verbose:
    print('Updating indexes...', file=sys.stderr)
  
  ensure_indexes(variant_database)
  
  return

def update_local_frequencies(variant_database):
  """
  Update the local frequencies for each variant in the database.
  
  For each document id in the database we find all variants with the same 
  variant id. We count the number of variants and divide this number by the
  total number of cases.
  
  Args:
    variant_database  : A pymongo connection to the database
  
  """
  variant_collection = variant_database['variant']
  case_collection = variant_database['case']
  number_of_cases = case_collection.count()
  for variant in variant_collection.find():
    variant_id = variant['variant_id']
    variant['local_frequency'] = (variant_collection.find(
                                    {
                                        'variant_id':variant['variant_id']
                                    }
                                  ).count()) / number_of_cases
  return

def ensure_indexes(variant_database):
  """Function to check the necessary indexes."""
  variant_collection = variant_database['variant']
  variant_collection.ensure_index(
                [
                  ('case_id', ASCENDING),
                  ('variant_rank', ASCENDING),
                  ('variant_type', ASCENDING),
                  ('thousand_genomes_frequency', ASCENDING),
                  ('gene_lists', ASCENDING)
                ],
                background=True
      )
  variant_collection.ensure_index(
                [
                  ('hgnc_symbols', ASCENDING),
                  ('exac_frequency', ASCENDING),
                ],
                background=True
      )
    
  variant_collection.ensure_index(
                [
                  ('thousand_genomes_frequency', ASCENDING),
                  ('gene.functional_annotation', ASCENDING),
                  ('gene.region_annotation', ASCENDING)
                ],
                background=True
      )

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
  
  gene_lists = variant['info_dict'].get(
          config_object['GeneLists']['vcf_info_key'], 
          None
          )
  expected_inheritance = variant['info_dict'].get(
          config_object['ExpectedInheritanceModels']['vcf_info_key'], 
          []
          )
  
  disease_groups = variant['info_dict'].get(
          config_object['DiseaseGroups']['vcf_info_key'], 
          []
          )
  
  id_fields = [
                variant['CHROM'], 
                variant['POS'], 
                variant['REF'], 
                variant['ALT'], 
                variant_type
              ]
  
  variant_id = generate_md5_key(id_fields)
  document_id = generate_md5_key(id_fields+case_id.split('_'))

  # print(gene_lists)
  # print(expected_inheritance)

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
                          gene_lists = gene_lists,
                          expected_inheritance = expected_inheritance,
                          disease_groups = disease_groups
                  )
  
  # pp(json.loads(mongo_variant.to_json()))
  ################# Add the rank score and variant rank #################
  # Get the rank score as specified in the config file.
  # This is central for displaying variants in scout.
  mongo_variant['rank_score'] = float(
      variant.get('rank_scores', {}).get(case_name, 0.0)
    )
  
  mongo_variant['variant_rank'] = variant_count
  mongo_variant['quality'] = float(variant['QUAL'])
  mongo_variant['filters'] = variant['FILTER'].split(';')
  
  ################# Add gt calls #################
  gt_calls = []
  for individual in individuals:
    # This function returns an ODM GTCall object with the relevant information:
    gt_calls.append(get_genotype_information(
                                          variant,
                                          config_object,
                                          individual
                                        )
                                      )
  mongo_variant['samples'] = gt_calls

  ################# Add the compound information #################
  
  mongo_variant['compounds'] = get_compounds(
                                          variant,
                                          mongo_variant.rank_score,
                                          case,
                                          variant_type,
                                          config_object
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
  
  mongo_variant['genes'] = get_genes(variant)
  hgnc_symbols = set([])
  for gene in mongo_variant.genes:
    hgnc_symbols.add(gene.hgnc_symbol)
  
  mongo_variant['hgnc_symbols'] = list(hgnc_symbols)

  mongo_variant['ensemble_gene_ids'] = variant['info_dict'].get(
                              config_object['Ensembl_gene_id']['vcf_info_key'],
                              []
                            )
  
  ################# Add a list with the dbsnp ids #################
  
  mongo_variant['db_snp_ids'] = variant['ID'].split(';')
  
  ################# Add the frequencies #################
  
  try:
    mongo_variant['thousand_genomes_frequency'] = float(
                                variant['info_dict'].get(
                                  config_object['1000GMAF']['vcf_info_key'],
                                  ['0'])[0]
                                )
  except ValueError:
    pass
  
  try:
    mongo_variant['exac_frequency'] = float(
                                variant['info_dict'].get(
                                  config_object['EXAC']['vcf_info_key'],
                                  ['0'])[0]
                                )
  except ValueError:
    pass
  
  # Add the severity predictions
  mongo_variant['cadd_score'] = float(
                          variant['info_dict'].get(
                            config_object['CADD']['vcf_info_key'],
                            ['0'])[0]
                          )
  # Add conservation annotation
  mongo_variant['gerp_conservation'] = variant['info_dict'].get(
                                  config_object['Gerp']['vcf_info_key'],
                                  []
                                )
  mongo_variant['phast_conservation'] = variant['info_dict'].get(
                                  config_object['PhastCons']['vcf_info_key'],
                                  []
                                )
  mongo_variant['phylop_conservation'] = variant['info_dict'].get(
                                  config_object['PhylopCons']['vcf_info_key'],
                                  []
                                )

  # print('Variant:')
  # pp(json.loads(mongo_variant.to_json()))
  # print('')

  return mongo_variant


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
  """
  Take a case file and return the case on the specified format.

  Args:
    ped_file    : The path to a ped file
    family_type : A string that describe the format of the ped file
    institute_name  : A string that represents the name of the institute
                      that the family belongs to.

  Returns:
    cases : A list with mongo engine objects that describe the cases
            found in the pedigree file.
  """
  # Use ped_parser to get information from the pedigree file
  case_parser = FamilyParser(ped_file, family_type=family_type)
  # Cases is a list that will hold all cases found in the ped file
  cases = []
  for case in case_parser.to_json():
    # Create a mongo engine case
    mongo_case = Case(case_id = '_'.join([institute_name, case['family_id']]))
    # We use the family id as display name for scout
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

def get_genotype_information(variant, config_object, individual):
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

def get_transcript_information(vep_entry):
  """
  Create a mongo engine transcript object and fill it with the relevant information

  Args:
    vep_entry : A vep entry parsed by vcf_parser

  Returns:
    transcript  : A mongo engine transcript object
  """
  # There can be several functional annotations for one variant
  functional_annotations = vep_entry.get('Consequence', '').split('&')
  # Get the transcript id
  transcript_id = vep_entry.get('Feature', '').split(':')[0]
  # Create a mongo engine transcript object
  transcript = Transcript(transcript_id = transcript_id)
  transcript.hgnc_symbol = vep_entry.get('SYMBOL', '').split('.')[0]
  # Fill it with the available information
  if vep_entry.get('PolyPhen', None):
    transcript.polyphen_prediction = vep_entry['PolyPhen']
  if vep_entry.get('SIFT', None):
    transcript.sift_prediction = vep_entry['SIFT']
  if vep_entry.get('EXON', None):
    transcript.exon = vep_entry['EXON']
  if vep_entry.get('INTRON', None):
    transcript.intron = vep_entry['INTRON']

  coding_sequence_entry = vep_entry.get('HGVSc', '').split(':')
  protein_sequence_entry = vep_entry.get('HGVSp', '').split(':')

  # If there is a coding sequence entry we need to parse it:
  coding_sequence_name = None
  if len(coding_sequence_entry) > 1:
    coding_sequence_name = coding_sequence_entry[-1].split('.')[1]

  if coding_sequence_name:
    transcript.coding_sequence_name = coding_sequence_name

  # If there is a protein sequence entry we need to parse it:
  protein_sequence_name = None
  if len(protein_sequence_entry) > 1:
    protein_sequence_name = protein_sequence_entry[-1].split('.')[1]

  if protein_sequence_name:
    transcript.protein_sequence_name = protein_sequence_name
  
  functional = []
  regional = []
  for annotation in functional_annotations:
    functional.append(annotation)
    regional.append(SO_TERMS[annotation]['region'])
  
  transcript.functional_annotations = functional
  transcript.region_annotations = regional

  return transcript


def get_genes(variant):
  """
  Get the transcript information in the mongoengine format.

  Args:
    variant : A Variant dictionary

  Returns:
    mongo_genes: A list with mongo engine object that represents the genes

  """
  genes = {}
  transcripts = []
  mongo_genes = []
  # We need to keep track of the highest ranked gene in order to know what to
  # display in the variant overwiew in scout
  best_rank = None
  # vep_info is a list of dictionarys with vep entrys
  # Each vep entry represents a transcript so one transcript belongs to one gene
  for vep_entry in variant['vep_info'].get(variant['ALT'], []):
    # We should first check if the variant is in a genetic region
    # If it is not we do not add any entry
    functional_annotations = vep_entry.get('Consequence', '').split('&')
    # Check if any of the consequences are genetic
    genetic_region = False
    for annotation in functional_annotations:
      region = SO_TERMS[annotation]['region']
      # If any of the functional annotations are genetic we wnat to show it
      if region in GENETIC_REGIONS:
        genetic_region = True
    
    # If any of the annotations are in genetic regions we add the information.
    if genetic_region:
    
      transcripts.append(get_transcript_information(vep_entry))
  
  # We now need to find the most severe transcript for each gene:
  for transcript in transcripts:
    transcript_id = transcript.transcript_id
    hgnc_symbol = transcript.hgnc_symbol
    for i, functional_annotation in enumerate(transcript.functional_annotations):
      rank = SO_TERMS[functional_annotation]['rank']
      
      if hgnc_symbol not in genes:
        genes[hgnc_symbol] = {
                        'most_severe_transcript': transcript,
                        'most_severe_function': functional_annotation,
                        'most_severe_region': transcript.region_annotations[i],
                        'best_rank' : rank,
                        'transcripts': {
                                  transcript_id : transcript
                                  }
                          }
      else:
        genes[hgnc_symbol]['transcripts'][transcript_id] = transcript
        if rank < best_rank:
          genes[hgnc_symbol]['most_severe_transcript'] = transcript
          genes[hgnc_symbol]['most_severe_function'] = functional_annotation
          genes[hgnc_symbol]['most_severe_region'] = transcript.region_annotations[i]
          best_rank = rank
  
  
  for gene in genes:
    most_severe = genes[gene]['most_severe_transcript']
    # Create a mongo engine gene object for each gene found in the variant
    mongo_gene = Gene(hgnc_symbol=gene)
    # Add a list with the transcripts:
    mongo_gene.transcripts = []
    for transcript_id in genes[gene]['transcripts']:
      mongo_gene.transcripts.append(genes[gene]['transcripts'][transcript_id])
    
    try:
      mongo_gene.functional_annotation = genes[gene]['most_severe_function']
    except AttributeError:
      pass
    try:
      mongo_gene.region_annotation = genes[gene]['most_severe_region']
    except AttributeError:
      pass
    try:
      mongo_gene.sift_prediction = most_severe.sift_prediction
    except AttributeError:
      pass
    try:
      mongo_gene.polyphen_prediction = most_severe.polyphen_prediction
    except AttributeError:
      pass
    # Add the mongo engine gene to the dictionary
    mongo_genes.append(mongo_gene)
  
  return mongo_genes

def get_compounds(variant, rank_score, case, variant_type, config_object):
  """
  Get a list with mongoengine compounds for this variant.
  
  Arguments:
    variant       : A Variant dictionary
    rank_score    : The rank score for the variant
    case          : A case object
    variant_type  : 'research' or 'clinical'
    config_object : A config object with the information from the config file
  
  Returns:
    compounds     : A list of mongo engine compound objects
  """
  case_id = case.case_id
  case_name = case.display_name
  
  compounds = []
  
  for compound in variant['compound_variants'].get(case_name, []):
    compound_name = compound['variant_id']
    # The compound id have to match the document id
    compound_id = generate_md5_key(
                            compound_name.split('_') +
                            [variant_type] +
                            case_id.split('_')
                  )
    try:
      compound_score = float(compound['compound_score'])
    except TypeError:
      compound_score = 0.0
    compound_individual_score = compound_score - rank_score
    mongo_compound = Compound(
                        variant=compound_id,
                        display_name = compound_name,
                        rank_score = compound_individual_score,
                        combined_score = compound_score
                      )
    
    compounds.append(mongo_compound)
  
  return compounds

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
                help="Path to the config file for loading the variants."
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
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(vcf_file, ped_file, config_file, family_type, mongo_db, username,
        variant_type, madeline, password, institute, verbose):
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
                      mongo_db=mongo_db, username=username, password=password, 
                      variant_type=variant_type, madeline_file=madeline, 
                      institute_name=institute, verbose=verbose)


if __name__ == '__main__':
    cli()
