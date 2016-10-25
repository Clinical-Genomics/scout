#!/usr/bin/env python
# encoding: utf-8
"""
load_hgnc.py

Build a file with genes that are based on hgnc format.
Parses ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt,
ftp.broadinstitute.org/pub/ExAC_release//release0.3/functional_gene_constraint/
and a biomart dumb from ensembl with
'Gene ID' 'Chromosome' 'Gene Start' 'Gene End' 'HGNC symbol'

The hgnc file will determine which genes that are added and most of the meta information.
The ensembl gene file will add coordinates and the exac file will add pLi scores.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
from codecs import open
import gzip
import logging

import click

from scout.load import load_hgnc_genes

logger = logging.getLogger(__name__)

@click.command()
@click.option('--hgnc',
                type=click.Path(exists=True),
                help="Path to hgnc file",
)
@click.option('--ensembl',
                type=click.Path(exists=True),
                help="Path to ensembl transcripts file",
)
@click.option('--exac',
                type=click.Path(exists=True),
                help="Path to exac gene file",
)
@click.option('--hpo',
                type=click.Path(exists=True),
                help="Path to HPO gene file",
)
@click.option('--export-genes',
                is_flag=True,
                help="Export all genes from the database"
)
@click.option('--export-transcripts',
                is_flag=True,
                help="Export all refseq transcripts from the database"
)
@click.pass_context
def genes(ctx, hgnc, ensembl, exac, hpo, export_genes, export_transcripts):
    """
    Load the hgnc aliases to the mongo database.
    """
    adapter=ctx.obj['adapter']
    if export_genes:
        print("#Chrom\tStart\tEnd\thgnc_symbol")
        for gene in adapter.hgnc_genes():
            gene_string = ("{0}\t{1}\t{2}\t{3}")
            print(gene_string.format(
                gene.chromosome,
                gene.start,
                gene.end,
                gene.hgnc_symbol
            ))
    
    elif export_transcripts:
        print("#Chrom\tStart\tEnd\tTranscript\tRefSeq\thgnc_symbol")
        for gene in adapter.hgnc_genes():
            for transcript in gene.transcripts:
                transcript_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}")
                print(transcript_string.format(
                    gene.chromosome,
                    transcript.start,
                    transcript.end,
                    transcript.ensembl_transcript_id,
                    transcript.refseq_id,
                    gene.hgnc_symbol
                ))
            
    
    else:
        if not (hgnc and ensembl and exac and hpo):
            logger.info("Please provide all gene files")
            ctx.abort()
    
        logger.info("Loading hgnc file from {0}".format(hgnc))
        if hgnc.endswith('.gz'):
            hgnc_handle = gzip.open(hgnc, 'r')
        else:
            hgnc_handle = open(hgnc, 'r')
        
        logger.info("Loading ensembl transcript file from {0}".format(
                    ensembl))
        if ensembl.endswith('.gz'):
            ensembl_handle = gzip.open(ensembl, 'r')
        else:
            ensembl_handle = open(ensembl, 'r')
        
        logger.info("Loading exac gene file from {0}".format(
                    exac))
        if exac.endswith('.gz'):
            exac_handle = gzip.open(exac, 'r')
        else:
            exac_handle = open(exac, 'r')
        
        logger.info("Loading HPO gene file from {0}".format(
                    hpo))
        if hpo.endswith('.gz'):
            hpo_handle = gzip.open(hpo, 'r')
        else:
            hpo_handle = open(hpo, 'r')
        
        load_hgnc_genes(
            adapter=adapter,
            ensembl_transcripts=ensembl_handle, 
            hgnc_genes=hgnc_handle, 
            exac_genes=exac_handle,
            hpo_lines=hpo_handle
        )