# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

from click import progressbar

from scout.build import build_hgnc_gene
from scout.utils.link import link_genes

LOG = logging.getLogger(__name__)


def load_hgnc_genes(adapter, ensembl_lines, hgnc_lines, exac_lines, mim2gene_lines,
                    genemap_lines, hpo_lines, build='37'):
    """Load genes into the database
        
    link_genes will collect information from all the different sources and 
    merge it into a dictionary with hgnc_id as key and gene information as values.

    Args:
        adapter(MongoAdapter)
    
    Returns:
        gene_objects(list): A list with all gene_objects that was loaded into database
    """
    gene_objects = list()
    # Link the resources
    genes = link_genes(
        ensembl_lines=ensembl_lines,
        hgnc_lines=hgnc_lines,
        exac_lines=exac_lines,
        mim2gene_lines=mim2gene_lines,
        genemap_lines=genemap_lines,
        hpo_lines=hpo_lines
    )

    non_existing = 0
    nr_genes = len(genes)
    
    with progressbar(genes.values(), label="Building genes", length=nr_genes) as bar:
        for gene_data in bar:
            if not gene_data.get('chromosome'):
                LOG.debug("skipping gene: %s. No coordinates found", gene_data['hgnc_symbol'])
                non_existing += 1
                continue
        
            gene_obj = build_hgnc_gene(gene_data, build=build)
            gene_objects.append(gene_obj)

    LOG.info("Loading genes build %s", build)
    adapter.load_hgnc_bulk(gene_objects)

    LOG.info("Loading done. %s genes loaded", len(gene_objects))
    LOG.info("Nr of genes without coordinates in build %s: %s", build,non_existing)
    
    return gene_objects
