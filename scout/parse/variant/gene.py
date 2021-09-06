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


def parse_genes(transcripts):
    """Parse transcript information and get the gene information from there.

    Use hgnc_id as identifier for genes and ensembl transcript id to identify transcripts.

    First group all transcripts on gene. Choose to group by hgnc id when available, otherwise
    hgnc symbol. If no gene identifier we skip the transcript.

    Then go through all transcript for every gene and find out which one that has the most severe
    consequence.

    Args:
        transcripts(iterable(dict))

    Returns:
      genes (list(dict)): A list with dictionaries that represents genes

    """
    genes_to_transcripts = {}
    for transcript in transcripts:
        hgnc_id = transcript["hgnc_id"]
        hgnc_symbol = transcript["hgnc_symbol"]

        gene_identifier = hgnc_id or hgnc_symbol
        if not gene_identifier:
            continue

        if gene_identifier not in genes_to_transcripts:
            genes_to_transcripts[gene_identifier] = []
        genes_to_transcripts[gene_identifier].append(transcript)

    # List with all genes and their transcripts
    genes = []

    hgvs_identifier = None
    canonical_transcript = None
    exon = None

    # Loop over all genes
    for gene_id in genes_to_transcripts:
        # Get the transcripts for a gene
        gene_transcripts = genes_to_transcripts[gene_id]
        # This will be a consequece from SO_TERMS
        most_severe_consequence = None
        # Set the most severe score to infinity
        most_severe_rank = float("inf")
        # The most_severe_transcript is a dict
        most_severe_transcript = None

        most_severe_region = None

        most_severe_sift = None
        most_severe_polyphen = None

        hgvs_identifier = None
        exon = None
        canonical_transcript = None

        # Loop over all transcripts for a gene to check which is most severe
        for transcript in gene_transcripts:
            hgnc_id = transcript["hgnc_id"]
            hgnc_symbol = transcript["hgnc_symbol"]
            if not hgvs_identifier:
                hgvs_identifier = transcript.get("coding_sequence_name")
            if not canonical_transcript:
                canonical_transcript = transcript["transcript_id"]
            if not exon:
                exon = transcript["exon"]

            # Loop over the consequences for a transcript
            for consequence in transcript["functional_annotations"]:
                # Get the rank based on SO_TERM
                # Lower rank is worse
                new_rank = SO_TERMS[consequence]["rank"]

                if new_rank > most_severe_rank:
                    continue
                # If a worse consequence is found, update the parameters
                most_severe_rank = new_rank
                most_severe_consequence = consequence
                most_severe_transcript = transcript
                most_severe_sift = transcript["sift_prediction"]
                most_severe_polyphen = transcript["polyphen_prediction"]
                most_severe_region = SO_TERMS[consequence]["region"]

            if transcript["is_canonical"] and transcript.get("coding_sequence_name"):
                hgvs_identifier = transcript.get("coding_sequence_name")
                canonical_transcript = transcript["transcript_id"]
                exon = transcript["exon"]

        gene = {
            "transcripts": gene_transcripts,
            "most_severe_transcript": most_severe_transcript,
            "most_severe_consequence": most_severe_consequence,
            "most_severe_sift": most_severe_sift,
            "most_severe_polyphen": most_severe_polyphen,
            "hgnc_id": hgnc_id,
            "hgnc_symbol": hgnc_symbol,
            "region_annotation": most_severe_region,
            "hgvs_identifier": hgvs_identifier,
            "canonical_transcript": canonical_transcript,
            "exon": exon,
        }
        genes.append(gene)

    return genes
