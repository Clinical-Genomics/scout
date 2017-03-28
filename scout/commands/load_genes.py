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

from scout.load import load_hgnc_genes
from scout.resources import (hgnc_path, exac_path, transcripts37_path, 
                             transcripts38_path, hpogenes_path)


from scout.utils.link import link_genes
from scout.utils.handle import get_file_handle

logger = logging.getLogger(__name__)

@click.command('genes', short_help='Load all genes')
@click.option('--hgnc',
                type=click.Path(exists=True),
                default=hgnc_path,
                help="Path to hgnc file",
)
@click.option('--ensembl37',
                type=click.Path(exists=True),
                default=transcripts37_path,
                help="Path to ensembl transcripts build 37 file",
)
@click.option('--ensembl38',
                type=click.Path(exists=True),
                default=transcripts38_path,
                help="Path to ensembl transcripts build 38 file",
)
@click.option('--exac',
                type=click.Path(exists=True),
                default=exac_path,
                help="Path to exac gene file",
)
@click.option('--hpo',
                type=click.Path(exists=True),
                default=hpogenes_path,
                help="Path to HPO gene file",
)
@click.option('--update',
                is_flag=True,
                help="If the gene set should be rebuilded"
)
@click.option('--build',
                type=click.Choice(['37', '38']),
                default='37',
                help="If the gene set should be rebuilded"
)
@click.pass_context
def genes(ctx, hgnc, ensembl37, ensembl38, exac, hpo, update, build):
    """
    Load the hgnc genes to the mongo database.
    """
    adapter=ctx.obj['adapter']

    #Test if the genes are loaded
    if build == '37':
        ensembl = ensembl37
    else:
        ensembl = ensembl38

    nr_genes = adapter.hgnc_gene(build=build).count()
    logger.info("Nr of genes in build %s: %s" % (build, nr_genes))
    if nr_genes != 0:
        if update:
            logger.warning("Dropping all gene information")
            adapter.drop_genes(build)
            logger.info("Genes dropped")
        else:
            logger.info("Genes are already loaded")
            logger.info("If you wish to update genes use '--update'")
            ctx.abort()

    if not (hgnc and ensembl and exac and hpo):
        logger.info("Please provide all gene files")
        ctx.abort()

    logger.info("Loading hgnc file from {0}".format(hgnc))
    hgnc_lines = get_file_handle(hgnc)

    logger.info("Loading ensembl transcript file from {0}".format(
                ensembl))
    ensembl_lines = get_file_handle(ensembl)

    logger.info("Loading exac gene file from {0}".format(
                exac))
    exac_lines = get_file_handle(exac)

    logger.info("Loading HPO gene file from {0}".format(
                hpo))
    hpo_lines = get_file_handle(hpo)

    genes = link_genes(
        ensembl_lines=ensembl_lines,
        hgnc_lines=hgnc_lines,
        exac_lines=exac_lines,
        hpo_lines=hpo_lines,
    )

    load_hgnc_genes(
        adapter=adapter,
        genes=genes,
        build=build
    )