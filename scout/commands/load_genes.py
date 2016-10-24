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
                required=True
)
@click.option('--ensembl',
                type=click.Path(exists=True),
                help="Path to ensembl transcripts file",
                required=True
)
@click.option('--exac',
                type=click.Path(exists=True),
                help="Path to exac gene file",
                required=True
)
@click.option('--hpo',
                type=click.Path(exists=True),
                help="Path to HPO gene file",
                required=True
)
@click.pass_context
def genes(ctx, hgnc, ensembl, exac, hpo):
    """
    Load the hgnc aliases to the mongo database.
    """
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
        adapter=ctx.obj['adapter'],
        ensembl_transcripts=ensembl_handle, 
        hgnc_genes=hgnc_handle, 
        exac_genes=exac_handle,
        hpo_lines=hpo_handle
    )