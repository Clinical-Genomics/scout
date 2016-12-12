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
from scout.parse.transcript import (parse_transcripts)

def parse_genes(variant):
    """Get the gene from transcripts.
    
        Args:
          variant(dict)
    
        Returns:
          genes (list(dict)): A list with dictionaries that represents genes
    
    """
    transcripts = parse_transcripts(variant)
    
    genes_to_transcripts = {}
    genes = []

    # Group all transcripts by gene
    for transcript in transcripts:
        hgnc_id = transcript['hgnc_id']

        if hgnc_id:
            if hgnc_id in genes_to_transcripts:
                genes_to_transcripts[hgnc_id].append(transcript)
            else:
                genes_to_transcripts[hgnc_id] = [transcript]

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
            'hgnc_id': gene_id,
            'region_annotation': SO_TERMS[most_severe_consequence]['region'],
        }
        genes.append(gene)    

    return genes
