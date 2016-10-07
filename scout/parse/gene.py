#!/usr/bin/env python
# encoding: utf-8
"""
get_genes.py

Parse all information for genes and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""
import logging

from scout.constants import SO_TERMS
from . import (get_omim_gene_ids, get_omim_phenotype_ids, parse_transcripts,
               parse_disease_associated)

def parse_gene_descriptions(variant):
    """Get the gene descriptions for the variant
    
        Args:
            variant(dict): A Variant dictionary
        
        Returns:
            descriptions(dict): Dict with {hgcn_symbol: description}
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

def parse_genes(variant):
    """Get the gene from transcripts.
    
        Args:
          variant(dict)
    
        Returns:
          genes (list(dict)): A list with mongo engine object that 
                              represents the genes
    
    """
    transcripts = parse_transcripts(variant)
    disease_associated_transcripts = parse_disease_associated(variant)
    genes_to_transcripts = {}
    genes = []

    # Get the omim ids for each gene
    mim_ids = get_omim_gene_ids(variant)

    # Get the phenotype ids for each gene
    phenotype_mim_ids = get_omim_phenotype_ids(variant)

    # A dictionary with clinical gene descriptions
    gene_descriptions = parse_gene_descriptions(variant)

    # Genes can have reduced penetrance
    reduced_penetrance = set(variant['info_dict'].get('Reduced_penetrance', []))

    # Group all transcripts by gene
    for transcript in transcripts:
        hgnc_symbol = transcript['hgnc_symbol']
        ensembl_gene_id = transcript['ensembl_id']
        if hgnc_symbol in genes_to_transcripts:
            genes_to_transcripts[hgnc_symbol].append(transcript)
        else:
            genes_to_transcripts[hgnc_symbol] = [transcript]

    # We need to find out the most severe consequence in all transcripts
    # and save in what transcript we found it
    for gene_id in genes_to_transcripts:
        gene_transcripts = genes_to_transcripts[gene_id]
        most_severe_consequence = None
        most_severe_score = 100
        most_severe_transcript = None
        most_severe_sift = None
        most_severe_polyphen = None
        for transcript in gene_transcripts:
            ensembl_gene_id = transcript['ensembl_id']
            for consequence in transcript['functional_annotations']:
                new_score = SO_TERMS[consequence]['rank']
                if new_score < most_severe_score:
                    most_severe_score = new_score
                    most_severe_consequence = consequence
                    most_severe_transcript = transcript
                    most_severe_sift = transcript['sift_prediction']
                    most_severe_polyphen = transcript['polyphen_prediction']

        gene = {
            'transcripts': transcripts,
            'most_severe_transcript': most_severe_transcript,
            'most_severe_consequence': most_severe_consequence,
            'most_severe_sift': most_severe_sift,
            'most_severe_polyphen': most_severe_polyphen,
            'hgnc_symbol': gene_id,
            'ensembl_gene_id': ensembl_gene_id,
            'region_annotation': SO_TERMS[most_severe_consequence]['region'],
            'description': gene_descriptions.get(gene_id, ''),
        }
        genes.append(gene)    

    ######################################################################
    ## There are two types of OMIM terms, one is the OMIM gene entry    ##
    ## and one is for the phenotypic terms.                             ##
    ## Each key in the 'omim_terms' dictionary reprecents a gene id.    ##
    ## Values are a dictionary with 'omim_gene_id' = omim_gene_id and   ##
    ## 'phenotypic_terms' = [list of OmimPhenotypeObjects]              ##
    ######################################################################
    
    for gene in genes:
        hgnc_symbol = gene['hgnc_symbol']
        # Fill in the gene mim id
        if hgnc_symbol in mim_ids:
            gene['omim_gene_id'] = mim_ids[hgnc_symbol]
        else:
            gene['omim_gene_id'] = None
        # Add the associated phenotpyes
        if hgnc_symbol in phenotype_mim_ids:
            gene['phenotype_terms'] = phenotype_mim_ids[hgnc_symbol]
        else:
            gene['phenotype_terms'] = None
        
        if hgnc_symbol in reduced_penetrance:
            gene['reduced_penetrance'] = True
        else:
            gene['reduced_penetrance'] = False
        
        if hgnc_symbol in disease_associated_transcripts:
            gene['disease_associated'] = disease_associated_transcripts[hgnc_symbol]
        else:
            gene['disease_associated'] = None
            

    return genes
    