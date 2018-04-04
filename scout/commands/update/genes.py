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

from scout.load import load_hgnc_genes
from scout.resources import (hgnc_path, exac_path, transcripts37_path,
                             transcripts38_path, hpogenes_path)


from scout.utils.link import link_genes
from scout.utils.handle import get_file_handle

LOG = logging.getLogger(__name__)

@click.command('genes', short_help='Update all genes')
@click.option('--build',
                type=click.Choice(['37', '38']),
                help="What genome build should be used. If no choice update 37 and 38."
)
@click.option('--api-key', help='Specify the api key')
@click.pass_context
def genes(ctx, build, api_key):
    """
    Load the hgnc aliases to the mongo database.
    """
    adapter = ctx.obj['adapter']

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

    if build:
        builds = [build]
    else:
        builds = ['37', '38']
    
    for build in builds:
        LOG.info("Loading hgnc file from {0}".format(hgnc_path))
        hgnc_handle = get_file_handle(hgnc_path)
        
        ensembl_handle = None
        if build == '37':
            ensembl_handle = get_file_handle(transcripts37_path)

        elif build == '38':
            ensembl_handle = get_file_handle(transcripts38_path)

        LOG.info("Loading exac gene file from {0}".format(exac_path))
        exac_handle = get_file_handle(exac_path)

        hpo_handle = get_file_handle(hpogenes_path)
        
        genes = link_genes(
            ensembl_lines=ensembl_handle,
            hgnc_lines=hgnc_handle,
            exac_lines=exac_handle,
            mim2gene_lines=mim_files['mim2gene'],
            genemap_lines=mim_files['genemap'],
            hpo_lines=hpo_handle
        )
        
        load_hgnc_genes(adapter=adapter, genes=genes, build=build)
