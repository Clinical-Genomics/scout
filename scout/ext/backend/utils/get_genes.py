#!/usr/bin/env python
# encoding: utf-8
"""
get_genes.py

Parse all information for genes and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, unicode_literals, print_function,)

import sys
import os
import click

from ....models import (Gene, OmimPhenotype, GeneList)

from . import get_transcript


from pprint import pprint as pp

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
  
  # Conversion from ensembl to refseq
  # ensembl_to_refseq is a dictionary with ensembl transcript id as keys and
  # a list of refseq ids as values
  ensembl_to_refseq = {}
  for gene_info in variant['info_dict'].get(
    'Ensembl_transcript_to_refseq_transcript', []):
    splitted_gene = gene_info.split(':')
    transcript_info = splitted_gene[1]
    for transcript in transcript_info.split('|'):
      splitted_transcript = transcript.split('>')
      if len(splitted_transcript) > 1:
        ensembl_id = splitted_transcript[0]
        refseq_ids = splitted_transcript[1].split('/')
        ensembl_to_refseq[ensembl_id] = refseq_ids
  
  # A dictionary with clinical gene descriptions
  gene_descriptions = {}
  for gene_info in variant['info_dict'].get('Gene_description', []):
    splitted_gene = gene_info.split(':')
    hgnc_symbol = splitted_gene[0]
    description = splitted_gene[1]
    gene_descriptions[hgnc_symbol] = description
  
  # First we get all vep entrys that we find and put them under their 
  # corresponding gene symbol in 'genes'
  for vep_entry in variant['vep_info'].get(variant['ALT'], []):
      transcript = get_transcript(vep_entry, ensembl_to_refseq)
      hgnc_symbol = transcript.hgnc_symbol
      if hgnc_symbol:
        if hgnc_symbol in genes:
          genes[hgnc_symbol]['transcripts'][transcript.transcript_id] = transcript
          for functional_annotation in transcript.functional_annotations:
            new_rank = SO_TERMS[functional_annotation]['rank']
            if new_rank < genes[hgnc_symbol]['best_rank']:
              genes[hgnc_symbol]['best_rank'] = new_rank
              genes[hgnc_symbol]['most_severe_transcript'] = transcript
              genes[hgnc_symbol]['most_severe_function'] = functional_annotation
              
        else:
          genes[hgnc_symbol] = {}
          genes[hgnc_symbol]['transcripts'] = {}
          genes[hgnc_symbol]['transcripts'][transcript.transcript_id] = transcript
          genes[hgnc_symbol]['most_severe_transcript'] = transcript
          genes[hgnc_symbol]['omim_gene_id'] = None
          genes[hgnc_symbol]['phenotypic_terms'] = []
          genes[hgnc_symbol]['best_rank'] = 40
          genes[hgnc_symbol]['ensembl_id'] = transcript.ensembl_id
          
          for functional_annotation in transcript.functional_annotations:
            new_rank = SO_TERMS[functional_annotation]['rank']
            if new_rank < genes[hgnc_symbol]['best_rank']:
              genes[hgnc_symbol]['best_rank'] = new_rank
              genes[hgnc_symbol]['most_severe_function'] = functional_annotation
  
  
  ######################################################################
  ## There are two types of OMIM terms, one is the OMIM gene entry    ##
  ## and one is for the phenotypic terms.                             ##
  ## Each key in the 'omim_terms' dictionary reprecents a gene id.    ##
  ## Values are a dictionary with 'omim_gene_id' = omim_gene_id and   ##
  ## 'phenotypic_terms' = [list of OmimPhenotypeObjects]              ##
  ######################################################################

  # Fill the omim gene id:s:
  for annotation in variant['info_dict'].get('OMIM_morbid', []):
    if annotation:
      splitted_record = annotation.split(':')
      try:
        hgnc_symbol = splitted_record[0]
        omim_term = int(splitted_record[1])
        genes[hgnc_symbol]['omim_gene_id'] = omim_term
      except (ValueError, KeyError):
        pass

  # Fill the omim phenotype terms:
  for gene_annotation in variant['info_dict'].get('Phenotypic_disease_model', []):
    if gene_annotation:
      splitted_gene = gene_annotation.split(':')
      hgnc_symbol = splitted_gene[0]
      for omim_entry in splitted_gene[1].split('|'):
        splitted_record = omim_entry.split('>')
        
        phenotype_id = int(splitted_record[0])
        inheritance_patterns = []
        if len(splitted_record) > 1:
          inheritance_patterns = splitted_record[1].split('/')
        
        disease_model = OmimPhenotype(
                              omim_id=phenotype_id,
                              disease_models=inheritance_patterns
                            )
        
        genes[hgnc_symbol]['phenotypic_terms'].append(disease_model)
  
  for hgnc_symbol in genes:
    gene_info = genes[hgnc_symbol]
    most_severe = gene_info['most_severe_transcript']
    # Create a mongo engine gene object for each gene found in the variant
    mongo_gene = Gene(hgnc_symbol=hgnc_symbol)
    mongo_gene.description = gene_descriptions.get(hgnc_symbol)
    mongo_gene.ensembl_gene_id = gene_info.get('ensembl_id', None)
    mongo_gene.omim_gene_entry = gene_info.get(
                                      'omim_gene_id', 
                                      None
                                      )

    mongo_gene.omim_phenotypes = gene_info.get(
                                      'phenotypic_terms', 
                                      []
                                      )

    # Add a list with the transcripts:
    mongo_gene.transcripts = []
    for transcript_id in gene_info['transcripts']:
      mongo_gene.transcripts.append(gene_info['transcripts'][transcript_id])

    try:
      mongo_gene.functional_annotation = gene_info['most_severe_function']
    except AttributeError:
      pass
    try:
      mongo_gene.region_annotation = SO_TERMS[mongo_gene.functional_annotation]['region']
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


@click.command()
@click.option('-f', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def cli(vcf_file, verbose):
  """
  Test generating genes.
  """

  from vcf_parser import VCFParser
  
  vcf_parser = VCFParser(infile=vcf_file, split_variants=True)
  for variant in vcf_parser:
    genes = get_genes(variant)
    for gene in genes:
      print(gene.to_json())


if __name__ == '__main__':
    cli()
