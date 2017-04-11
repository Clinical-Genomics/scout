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
import logging

import click

from pprint import pprint as pp

from scout.load import load_hgnc_genes
from scout.resources import (hgnc_path, exac_path, transcripts37_path,
                             transcripts38_path, mim2gene_path, genemap2_path,
                             hpogenes_path)


from scout.utils.link import link_genes
from scout.utils.handle import get_file_handle

logger = logging.getLogger(__name__)

@click.command('genes', short_help='Load all genes')
@click.option('--update',
                is_flag=True,
                help="If the gene set should be rebuilded"
)
@click.option('--build',
                type=click.Choice(['37', '38']),
                default='37',
                show_default=True,
                help="What genome build should be used."
)
@click.pass_context
def genes(ctx, update, build):
    """
    Load the hgnc aliases to the mongo database.
    """
    adapter = ctx.obj['adapter']

    # Test if the genes are loaded
    nr_present_genes = adapter.nr_genes(build=build)
    if nr_present_genes > 0:
        if update:
            logger.warning("Dropping all gene information")
            adapter.drop_genes()
            logger.info("Genes dropped")
        else:
            logger.info("Genes are already loaded")
            logger.info("If you wish to update genes use '--update'")
            ctx.abort()

    logger.info("Loading hgnc file from {0}".format(hgnc_path))
    hgnc_handle = get_file_handle(hgnc_path)

    if build == '37':
        logger.info("Loading ensembl transcript file from {0}".format(
                    transcripts37_path))
        ensembl_handle = get_file_handle(transcripts37_path)
    else:
        ensembl_handle = get_file_handle(transcripts38_path)

    logger.info("Loading exac gene file from {0}".format(
                exac_path))
    exac_handle = get_file_handle(exac_path)

    logger.info("Loading mim information from files {0}, {1}".format(
                mim2gene_path, genemap2_path))

    mim2gene_handle = get_file_handle(mim2gene_path)
    genemap_handle = get_file_handle(genemap2_path)
    hpo_handle = get_file_handle(hpogenes_path)

    genes = link_genes(
        ensembl_lines=ensembl_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_handle
    )

    load_hgnc_genes(adapter=adapter, genes=genes, build=build)
