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

from scout.resources import (hgnc_path, exac_path, transcripts37_path,
                             transcripts38_path, mim2gene_path, genemap2_path,
                             hpogenes_path)


from scout.utils.handle import get_file_handle

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
@click.pass_context
def genes(context, update, build):
    """
    Load the hgnc aliases to the mongo database.
    """
    builds = [build] if build else ['37', '38']
    builds = [build] if build else ['37']
    ensembl_genes_37_path = './local/ensembl/ensembl_genes_37.tsv'
    ensembl_genes_38_path = './local/ensembl/ensembl_genes_38.tsv'
    ensembl_transcripts_37_path = './local/ensembl/ensembl_transcripts_37.tsv'
    ensembl_transcripts_38_path = './local/ensembl/ensembl_transcripts_38.tsv'
    ensembl_exons_37_path = './local/ensembl/ensembl_exons_37.tsv'
    
    files = {
        '37': {
            'genes': ensembl_genes_37_path,
            'transcripts': ensembl_transcripts_37_path,
            'exons': ensembl_exons_37_path,
        },
        '38': {
            'genes': ensembl_genes_38_path,
            'transcripts': ensembl_transcripts_38_path
        },
    }
    
    adapter = context.obj['adapter']
    
    LOG.info("Loading hgnc file from {0}".format(hgnc_path))
    hgnc_handle = get_file_handle(hgnc_path)
    LOG.info("Loading omim information from files {0}, {1}".format(
                mim2gene_path, genemap2_path))
    mim2gene_handle = get_file_handle(mim2gene_path)
    genemap_handle = get_file_handle(genemap2_path)
    hpo_handle = get_file_handle(hpogenes_path)
    LOG.info("Loading exac gene file from {0}".format(
                exac_path))
    exac_handle = get_file_handle(exac_path)
    # Test if the genes are loaded
    for build in builds:
        nr_present_genes = adapter.nr_genes(build=build)
        if nr_present_genes > 0:
            if not update:
                LOG.info("Genes are already loaded")
                LOG.info("If you wish to update genes use '--update'")
                context.abort()
            # LOG.warning("Dropping all genes for build %s", build)
            # adapter.drop_genes(build=build)
            # LOG.info("Genes dropped")
            # LOG.warning("Dropping all transcripts for build %s", build)
            # adapter.drop_transcripts(build=build)
            # LOG.info("Transcripts dropped")
            # LOG.warning("Dropping all exons for build %s", build)
            # adapter.drop_exons(build=build)
            # LOG.info("Exons dropped")

        LOG.info('Loading gene coordinates from: %s', files[build]['genes'])
        ensembl_genes_handle = get_file_handle(files[build]['genes'])
        LOG.info('Loading transcript coordinates from: %s', files[build]['transcripts'])
        ensembl_transcripts_handle = get_file_handle(files[build]['transcripts'])
        LOG.info('Loading exons from: %s', files[build]['exons'])
        ensembl_exons_handle = get_file_handle(files[build]['exons'])


        hgnc_genes = load_hgnc_genes(
            adapter=adapter,
            ensembl_lines=ensembl_genes_handle,
            hgnc_lines=hgnc_handle,
            exac_lines=exac_handle,
            mim2gene_lines=mim2gene_handle,
            genemap_lines=genemap_handle,
            hpo_lines=hpo_handle,
            build=build,
        )

        ensembl_genes = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj['ensembl_id']
            ensembl_genes[ensembl_id] = gene_obj

        transcripts = load_transcripts(adapter, ensembl_transcripts_handle, build, ensembl_genes)
        adapter.update_indexes()

        load_exons(adapter, ensembl_exons_handle, build)
