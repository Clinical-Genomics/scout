#!/usr/bin/env python
# encoding: utf-8
"""
update/genes.py

Build a file with genes that are based on hgnc format.
Parses ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt,
ftp.broadinstitute.org/pub/ExAC_release/release0.3/functional_gene_constraint/
and a biomart dump from ensembl with
'Gene ID' 'Chromosome' 'Gene Start' 'Gene End' 'HGNC symbol'

The hgnc file will determine which genes that are added and most of the meta information.
The ensembl gene file will add coordinates and the exac file will add pLi scores.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
import logging

import click

from pprint import pprint as pp

from scout.load import (load_hgnc_genes, load_transcripts, load_exons)

from scout.utils.link import link_genes
from scout.utils.handle import get_file_handle

from scout.utils.requests import (fetch_mim_files, fetch_hpo_genes, fetch_hgnc, fetch_ensembl_genes,
                                  fetch_exac_constraint, fetch_ensembl_transcripts)

LOG = logging.getLogger(__name__)

@click.command('genes', short_help='Update all genes')
@click.option('--build',
                type=click.Choice(['37', '38']),
                help="What genome build should be used. If no choice update 37 and 38."
)
@click.option('--api-key', help='Specify the api key')
@click.pass_context
def genes(context, build, api_key):
    """
    Load the hgnc aliases to the mongo database.
    """
    LOG.info("Running scout update genes")
    adapter = context.obj['adapter']

    # Fetch the omim information
    api_key = api_key or context.obj.get('omim_api_key')
    if not api_key:
        LOG.warning("Please provide a omim api key to load the omim gene panel")
        context.abort()

    try:
        mim_files = fetch_mim_files(api_key, mim2genes=True, morbidmap=True, genemap2=True)
    except Exception as err:
        LOG.warning(err)
        context.abort()

    LOG.warning("Dropping all gene information")
    adapter.drop_genes(build)
    LOG.info("Genes dropped")
    LOG.warning("Dropping all transcript information")
    adapter.drop_transcripts(build)
    LOG.info("transcripts dropped")

    hpo_genes = fetch_hpo_genes()
    
    if build:
        builds = [build]
    else:
        builds = ['37', '38']
    
    hgnc_lines = fetch_hgnc()
    exac_lines = fetch_exac_constraint()
    
    
    for build in builds:
        ensembl_genes = fetch_ensembl_genes(build=build)
        
        # load the genes
        hgnc_genes = load_hgnc_genes(
            adapter=adapter,
            ensembl_lines=ensembl_genes,
            hgnc_lines=hgnc_lines,
            exac_lines=exac_lines,
            mim2gene_lines=mim_files['mim2genes'],
            genemap_lines=mim_files['genemap2'],
            hpo_lines=hpo_genes,
            build=build,
        )

        ensembl_genes = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj['ensembl_id']
            ensembl_genes[ensembl_id] = gene_obj

        # Fetch the transcripts from ensembl
        ensembl_transcripts = fetch_ensembl_transcripts(build=build)
        
        transcripts = load_transcripts(adapter, ensembl_transcripts, build, ensembl_genes)

    adapter.update_indexes()
        
    LOG.info("Genes, transcripts and Exons loaded")