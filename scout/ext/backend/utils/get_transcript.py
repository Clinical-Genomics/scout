#!/usr/bin/env python
# encoding: utf-8
"""
get_transcript.py

Parse all information for genes and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, unicode_literals, print_function,)

import sys
import os

import click

from scout.models import Transcript
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


def get_transcript(vep_entry, ensembl_to_refseq={}):
  """
  Create a mongo engine transcript object and fill it with the relevant information
  
  Args:
    vep_entry (dict): A vep entry parsed by vcf_parser
    ensembl_to_refseq (dict): Conversion from ensembl ids ti refseq ids
  
  Returns:
    transcript  : A mongo engine transcript object
  
  """
  # There can be several functional annotations for one variant
  functional_annotations = vep_entry.get('Consequence', '').split('&')
  # Get the transcript id
  transcript_id = vep_entry.get('Feature', '').split(':')[0]
  # Create a mongo engine transcript object
  transcript = Transcript(transcript_id = transcript_id)
  # Add the refseq ids
  transcript.refseq_ids = ensembl_to_refseq.get(transcript_id, [])
  # Add the hgnc gene identifier
  transcript.hgnc_symbol = vep_entry.get('SYMBOL', '').split('.')[0]
  # Add the ensembl gene identifier
  transcript.ensembl_id = vep_entry.get('Gene', '')
  
  ########### Fill it with the available information ###########
  
  ### Protein specific annotations ###
  
  ## Protein ID ##
  if vep_entry.get('ENSP', None):
    transcript.protein_id = vep_entry['ENSP']
  
  if vep_entry.get('PolyPhen', None):
    transcript.polyphen_prediction = vep_entry['PolyPhen']
  if vep_entry.get('SIFT', None):
    transcript.sift_prediction = vep_entry['SIFT']
  if vep_entry.get('SWISSPROT', None):
    transcript.swiss_prot = vep_entry['SWISSPROT']
  
  if vep_entry.get('DOMAINS', None):
    pfam_domains = vep_entry['DOMAINS'].split('&')
    for annotation in pfam_domains:
      annotation = annotation.split(':')
      domain_name = annotation[0]
      domain_id = annotation[1]
      if domain_name == 'Pfam_domain':
        transcript.pfam_domain = domain_id
      elif domain_name == 'PROSITE_profiles':
        transcript.prosite_profile = domain_id
      elif domain_name == 'SMART_domains':
        transcript.smart_domain = domain_id
    
  
  coding_sequence_entry = vep_entry.get('HGVSc', '').split(':')
  protein_sequence_entry = vep_entry.get('HGVSp', '').split(':')
  
  coding_sequence_name = None
  if len(coding_sequence_entry) > 1:
    coding_sequence_name = coding_sequence_entry[-1]

  if coding_sequence_name:
    transcript.coding_sequence_name = coding_sequence_name

  protein_sequence_name = None
  if len(protein_sequence_entry) > 1:
    protein_sequence_name = protein_sequence_entry[-1]

  if protein_sequence_name:
    transcript.protein_sequence_name = protein_sequence_name
  
  
  if vep_entry.get('BIOTYPE', None):
    transcript.biotype = vep_entry['BIOTYPE']
  
  if vep_entry.get('EXON', None):
    transcript.exon = vep_entry['EXON']
  if vep_entry.get('INTRON', None):
    transcript.intron = vep_entry['INTRON']
  if vep_entry.get('STRAND', None):
    if vep_entry['STRAND'] == '1':
      transcript.strand = '+'
    elif vep_entry['STRAND'] == '-1':
      transcript.strand = '-'
  
  functional = []
  regional = []
  for annotation in functional_annotations:
    functional.append(annotation)
    regional.append(SO_TERMS[annotation]['region'])
  
  transcript.functional_annotations = functional
  transcript.region_annotations = regional
  
  return transcript


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
  Test the transcript class.
  """
  from vcf_parser import VCFParser
  
  vcf_parser = VCFParser(infile=vcf_file, split_variants=True)
  for variant in vcf_parser:
    
    # Conversion from ensembl to refseq
    # ensembl_to_refseq is a dictionary with ensembl transcript id as keys and
    # a list of refseq ids as values
    ensembl_to_refseq = {}
    for gene_info in variant['info_dict'].get('Ensembl_transcript_to_refseq_transcript', []):
      splitted_gene = gene_info.split(':')
      transcript_info = splitted_gene[1]
      for transcript in transcript_info.split('|'):
        splitted_transcript = transcript.split('>')
        if len(splitted_transcript) > 1:
          ensembl_id = splitted_transcript[0]
          refseq_ids = splitted_transcript[1].split('/')
          ensembl_to_refseq[ensembl_id] = refseq_ids
    
    for vep_entry in variant['vep_info'].get(variant['ALT'], []):
      transcript = get_transcript(vep_entry, ensembl_to_refseq)
      print(transcript.to_json())


if __name__ == '__main__':
    cli()
