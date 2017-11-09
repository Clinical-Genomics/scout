# -*- coding: utf-8 -*-
import logging

from pprint import pprint as pp

from click import progressbar

from scout.build import build_hgnc_gene
from scout.utils.link import link_genes

logger = logging.getLogger(__name__)


def load_hgnc_genes(adapter, ensembl_lines, hgnc_lines, exac_lines, mim2gene_lines,
                    genemap_lines, hpo_lines, build='37'):
    """Load genes with transcripts into the database

        Args:
            adapter(MongoAdapter)
        
        Returns:
            loaded_genes(list): A list with all gene_objects that was loaded into database
    """
    loaded_genes = list()
    # Link the resources
    genes = link_genes(
        ensembl_lines=ensembl_lines,
        hgnc_lines=hgnc_lines,
        exac_lines=exac_lines,
        mim2gene_lines=mim2gene_lines,
        genemap_lines=genemap_lines,
        hpo_lines=hpo_lines
    )

    logger.info("Loading the genes build %s", build)
    non_existing = 0
    nr_genes = len(genes)
    
    with progressbar(genes.values(), label="Loading genes", length=nr_genes) as bar:
        for gene_data in bar:
            if not gene_data.get('chromosome'):
                logger.debug("skipping gene: %s. No coordinates found", gene_data['hgnc_symbol'])
                non_existing += 1
                continue
        
            gene_obj = build_hgnc_gene(gene_data, build=build)
            adapter.load_hgnc_gene(gene_obj)
            loaded_genes.append(gene_obj)

    logger.info("Loading done. {0} genes loaded".format(len(loaded_genes)))
    logger.info("Nr of genes without coordinates in build {0}: {1}".format(build, non_existing))
    
    return loaded_genes
