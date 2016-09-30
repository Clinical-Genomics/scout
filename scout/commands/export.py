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
@click.option('-t', '--variant-type', default='causative')
@click.option('-f', '--format', default='vcf')
@click.option('-c', '--collaborator')
@click.pass_context
def export(ctx, institute, variant_type, collaborator, format):
    """
    Export variants from the mongo database.
    """
    logger.info("Running scout export")
    
    # Store variants in a dictionary
    causative_variants = {}
    
    adapter = ctx.obj['adapter']
    
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
        
    
