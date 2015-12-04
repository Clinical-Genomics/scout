#!/usr/bin/env python
# encoding: utf-8
"""
get_genes.py

Parse all information for genes and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""
import logging

from scout.models import (Gene, PhenotypeTerm, Transcript)

from . import get_transcript
from .constants import SO_TERMS

logger = logging.getLogger(__name__)

def create_ensembl_to_refseq(variant):
    """Create a dictionary with ensembleids to refseq ids
    
        Args:
            variant(dict): A Variant dictionary
        
        Returns:
            conversion(dict): Dict that translate the ids
    """
    info_key = 'Ensembl_transcript_to_refseq_transcript'
    conversion = {}
    vcf_entry = variant['info_dict'].get(info_key, [])
    
    for gene_info in vcf_entry:
        #Genes are splitted from transcripts with ':'
        splitted_gene = gene_info.split(':')
        transcript_info = splitted_gene[1]
        for transcript in transcript_info.split('|'):
            splitted_transcript = transcript.split('>')
            if len(splitted_transcript) > 1:
                ensembl_id = splitted_transcript[0]
                refseq_ids = splitted_transcript[1].split('/')
                conversion[ensembl_id] = refseq_ids
    return conversion
    
def get_hgnc_dict(variant, ensembl_to_refseq):
    """Get a dictionary with hgnc symbols as keys and a list of 
        transcripts as values
    
        Args:
            variant(dict): A Variant dictionary
            ensembl_to_refseq(dict): Conversion dict
        
        Returns:
            genes(dict)
    """
    pass

def get_gene_descriptions(variant):
    """Get the gene descriptions for the variant
    
        Args:
            variant(dict): A Variant dictionary
        
        Returns:
            descriptions(dict)
    """
    vcf_key = 'Gene_description'
    vcf_entry = variant['info_dict'].get(vcf_key, [])
    descriptions = {}
    for gene_info in vcf_entry:
        splitted_gene = gene_info.split(':')
        hgnc_symbol = splitted_gene[0]
        description = splitted_gene[1]
        descriptions[hgnc_symbol] = description
    
    return descriptions
        

def get_transcripts(variant):
    """Create a list of mongo engine transcript objects
    
        Args:
            vep_entry (dict): A vep entry parsed by vcf_parser
        
        Returns:
            transcripts(list(Transcript))
    """
    ensembl_to_refseq = create_ensembl_to_refseq(variant)
    transcripts = []
    
    for vep_entry in variant['vep_info'].get(variant['ALT'], []):
        # There can be several functional annotations for one variant
        functional_annotations = vep_entry.get('Consequence', '').split('&')
        # Get the transcript id
        transcript_id = vep_entry.get('Feature', '').split(':')[0]
        # Create a mongo engine transcript object
        transcript = Transcript(transcript_id = transcript_id)
        
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
        
        transcripts.append(transcript)
    
    return transcripts 

def get_omim_gene_ids(variant):
    """Get the mim ids for the genes
    
        Args:
            variant (dict): A Variant dictionary
        
        Returns:
            mim_ids(dict): hgnc_id as key and mim id as value
    """
    vcf_key = 'OMIM_morbid'
    vcf_entry = variant['info_dict'].get(vcf_key, [])
    
    mim_ids = {}
    for annotation in vcf_entry:
        if annotation:
            splitted_record = annotation.split(':')
            try:
                hgnc_symbol = splitted_record[0]
                omim_term = splitted_record[1]
                mim_ids[hgnc_symbol] = omim_term
            except (ValueError, KeyError):
                pass
    return mim_ids

def get_omim_phenotype_ids(variant):
    """Get the mim phenotype ids for the genes
    
        Args:
            variant (dict): A Variant dictionary
        
        Returns:
            phenotype_mim_ids(dict): hgnc_id as key and mim id as value
    """
    vcf_key = 'Phenotypic_disease_model'
    vcf_entry = variant['info_dict'].get(vcf_key, [])
    
    phenotype_mim_ids = {}
    for annotation in vcf_entry:
        if annotation:
            splitted_annotation = annotation.split(':')
            hgnc_symbol = splitted_annotation[0]
            splitted_entry = splitted_annotation[1].split('|')
            
            for record in splitted_entry:
                splitted_record = record.split('>')
                phenotype_id = splitted_record[0]
                inheritance_patterns = []
                if len(splitted_record) > 1:
                    inheritance_patterns = splitted_record[1].split('/')
          
                phenotype_term = PhenotypeTerm(
                                  phenotype_id=phenotype_id,
                                  disease_models=inheritance_patterns
                                )
                if hgnc_symbol in phenotype_mim_ids:
                    phenotype_mim_ids[hgnc_symbol].append(phenotype_term)
                else:
                    phenotype_mim_ids[hgnc_symbol] = [phenotype_term]
                    
    return phenotype_mim_ids

def get_genes(variant):
    """Get the gene information in the mongoengine format.
    
        Args:
          variant (dict): A Variant dictionary
    
        Returns:
          mongo_genes (list): A list with mongo engine object that 
                              represents the genes
    
    """
    genes = {}
    mongo_genes = []    
    
    transcripts = get_transcripts(variant)
    # A dictionary with clinical gene descriptions
    gene_descriptions = get_gene_descriptions(variant)
    
    # First we get all vep entrys that we find and put them under their
    # corresponding gene symbol in 'genes'
    
    for transcript in transcripts:
        hgnc_symbol = transcript.hgnc_symbol
        transcript_id = transcript.transcript_id
        functional_annotations = transcript.functional_annotations
        ensembl_id = transcript.ensembl_id
        
        if hgnc_symbol:
            if hgnc_symbol in genes:
                genes[hgnc_symbol]['transcripts'][transcript_id] = transcript
                # Check most severe transcript
                for functional_annotation in functional_annotations:
                    new_rank = SO_TERMS[functional_annotation]['rank']
                    if new_rank < genes[hgnc_symbol]['best_rank']:
                        genes[hgnc_symbol]['best_rank'] = new_rank
                        genes[hgnc_symbol]['most_severe_transcript'] = transcript
                        genes[hgnc_symbol]['most_severe_function'] = functional_annotation
            else:
                genes[hgnc_symbol] = {
                    'transcripts':{
                        transcript_id: transcript,
                    },
                    'most_severe_transcript': transcript,
                    'omim_gene_id': None,
                    'phenotypic_terms': [],
                    'best_rank': 100,
                    'ensembl_id': ensembl_id,
                }
    
                for functional_annotation in functional_annotations:
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
    
    # Fill the mim ids for the genes:
    mim_ids = get_omim_gene_ids(variant)
    for hgnc_symbol in mim_ids:
        if hgnc_symbol in genes:
            mim_id = mim_ids[hgnc_symbol]
            logger.debug("Adding mim id {0} to gene {1}".format(
                hgnc_symbol, mim_id))
            genes[hgnc_symbol]['omim_gene_id'] = mim_id
    
    # Fill the omim phenotype terms:
    
    phenotype_mim_ids = get_omim_phenotype_ids(variant)
    for hgnc_symbol in phenotype_mim_ids:
        phenotype_terms = phenotype_mim_ids[hgnc_symbol]
        if hgnc_symbol in genes:
            for term in phenotype_terms:
                genes[hgnc_symbol]['phenotypic_terms'].append(term)
    
    reduced_penetrance = set(variant['info_dict'].get('Reduced_penetrance', []))
    
    for hgnc_symbol in genes:
        gene_info = genes[hgnc_symbol]
        most_severe = gene_info['most_severe_transcript']
        # Create a mongo engine gene object for each gene found in the variant
        mongo_gene = Gene(hgnc_symbol=hgnc_symbol)
        if hgnc_symbol in reduced_penetrance:
            mongo_gene.reduced_penetrance = True
      
        mongo_gene.description = gene_descriptions.get(hgnc_symbol)
        mongo_gene.ensembl_gene_id = gene_info['ensembl_id']
        mongo_gene.omim_gene_entry = gene_info['omim_gene_id']
    
        mongo_gene.omim_phenotypes = gene_info['phenotypic_terms']
    
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
    