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

from scout.load import (load_hgnc_genes, load_transcripts, load_exons)

from scout.utils.requests import (fetch_ensembl_genes, fetch_hgnc, fetch_mim_files,
                                 fetch_exac_constraint, fetch_hpo_files, 
                                 fetch_ensembl_transcripts, fetch_ensembl_exons)

LOG = logging.getLogger(__name__)

@click.command('genes', short_help='Load all genes, transcripts and exons')
@click.option('--update',
                is_flag=True,
                help="If the gene set should be rebuilded"
)
@click.option('--build',
                type=click.Choice(['37', '38']),
                help="What genome build should be used. If none is choosen build both."
)
@click.option('--api-key', help='Specify the api key')
@click.pass_context
def genes(context, update, build, api_key):
    """
    Load the hgnc aliases to the mongo database.
    """
    builds = [build] if build else ['37', '38']
    api_key = api_key or context.obj.get('omim_api_key')
    
    if not api_key:
        LOG.warning("Please provide a api key to access OMIM data")
        LOG.info("Request a key from https://omim.org/downloads/")
        context.abort()
    
    adapter = context.obj['adapter']
    
    # Test if the genes are loaded
    for build in builds:
        nr_present_genes = adapter.nr_genes(build=build)
        if nr_present_genes == 0:
            LOG.info("No genes found for build %s", build)
            continue
        if not update:
            LOG.warning("Genes are already loaded")
            LOG.info("If you wish to update genes use '--update'")
            context.abort()
        LOG.warning("Dropping all genes for build %s", build)
        adapter.drop_genes(build=build)
        LOG.info("Genes dropped")
        LOG.warning("Dropping all transcripts for build %s", build)
        adapter.drop_transcripts(build=build)
        LOG.info("Transcripts dropped")
        LOG.warning("Dropping all exons for build %s", build)
        adapter.drop_exons(build=build)
        LOG.info("Exons dropped")
    
    try:
        # Fetch the latest hgnc version
        hgnc_lines = fetch_hgnc()
        
        # Fetch the neccessary omim files 
        mim_files = fetch_mim_files(api_key, mim2genes=True, genemap2=True)
        mim2gene_lines = mim_files['mim2genes']
        genemap_lines = mim_files['genemap2']
        
        # Fetch the hpo genes file
        hpo_files = fetch_hpo_files(hpogenes=True)
        hpo_lines = hpo_files['hpogenes']
        
        # Fetch exac file with pLi scores
        exac_lines = fetch_exac_constraint()
    except Exception as err:
        click.echo(err)
        context.abort()

    # Test if the genes are loaded
    for build in builds:
        
        ensembl_genes = fetch_ensembl_genes(build=build)
        
        # load the genes
        hgnc_genes = load_hgnc_genes(
            adapter=adapter,
            ensembl_lines=ensembl_genes,
            hgnc_lines=hgnc_lines,
            exac_lines=exac_lines,
            mim2gene_lines=mim2gene_lines,
            genemap_lines=genemap_lines,
            hpo_lines=hpo_lines,
            build=build,
        )
        
        ensembl_genes = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj['ensembl_id']
            ensembl_genes[ensembl_id] = gene_obj

        # Load the transcripts
        ensembl_transcripts = fetch_ensembl_transcripts(build=build)
        transcripts = load_transcripts(adapter, ensembl_transcripts, build, ensembl_genes)
        
        # Load the exons
        ensembl_exons = fetch_ensembl_exons(build=build)
        load_exons(adapter, ensembl_exons, build, ensembl_genes)
    
        adapter.update_indexes()
        
    LOG.info("Genes, transcripts and Exons loaded")