#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Export variants from a scout database

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging

import click

logger = logging.getLogger(__name__)

@click.command()
@click.option('-c', '--collaborator')
@click.option('--genes',
                is_flag=True,
                help="Export all genes from the database"
)
@click.option('--transcripts',
                is_flag=True,
                help="Export all refseq transcripts from the database"
)
@click.pass_context
def export(ctx, collaborator, genes, transcripts):
    """
    Export variants from the mongo database.
    """
    logger.info("Running scout export")
    adapter = ctx.obj['adapter']
    if genes:
        print("#Chrom\tStart\tEnd\tHgncSymbol\tHgncID")
        for gene in adapter.all_genes():
            gene_string = ("{0}\t{1}\t{2}\t{3}\t{4}")
            print(gene_string.format(
                gene.chromosome,
                gene.start,
                gene.end,
                gene.hgnc_symbol,
                gene.hgnc_id
            ))
    
    elif transcripts:
        print("#Chrom\tStart\tEnd\tTranscript\tRefSeq\tHgncSymbol\tHgncID")
        for gene in adapter.all_genes():
            for transcript in gene.transcripts:
                transcript_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}")
                print(transcript_string.format(
                    gene.chromosome,
                    transcript.start,
                    transcript.end,
                    transcript.ensembl_transcript_id,
                    transcript.refseq_id,
                    gene.hgnc_symbol,
                    gene.hgnc_id
                ))
    else:
        # Store variants in a dictionary to avoid duplicated
        causative_variants = {}

        vcf_header = [
            "##fileformat=VCFv4.2",
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
        ]
        
        for line in vcf_header:
            print(line)
        
        #put variants in a dict to get unique ones
        variants = {}
        for variant in adapter.get_causatives(institute_id=collaborator):
            variant_id = '_'.join(variant.variant_id.split('_')[:-1])
            variants[variant_id] = variant
        
        for variant_id in variants:
            variant = variants[variant_id]
            variant_line = [
                variant.chromosome,
                str(variant.position),
                ';'.join(variant.db_snp_ids),
                variant.reference,
                variant.alternative,
                str(variant.quality),
                ';'.join(variant.filters),
                '.',
            ]
            print('\t'.join(variant_line))
            
    
