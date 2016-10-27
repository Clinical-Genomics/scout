# -*- coding: utf-8 -*-
import logging

from datetime import datetime

from scout.utils.link import link_genes
from scout.build import build_hgnc_gene

logger = logging.getLogger(__name__)


def load_hgnc_genes(adapter, ensembl_lines, hgnc_lines, exac_lines, hpo_lines):
    """Load genes with transcripts into the database

        Args:
            adapter(MongoAdapter)
            ensembl_lines(iterable(str))
            hgnc_lines(iterable(str))
            exac_lines(iterable(str))
            hpo_lines(iterable(str))
    """
    genes = link_genes(
        ensembl_lines=ensembl_lines,
        hgnc_lines=hgnc_lines,
        exac_lines=exac_lines,
        hpo_lines=hpo_lines,
    )
    logger.info("Loading the genes and transcripts...")
    
    start_time = datetime.now()
    
    for nr_genes, hgnc_symbol in enumerate(genes):
        gene = genes[hgnc_symbol]
        gene_obj = build_hgnc_gene(gene)
        adapter.load_hgnc_gene(gene_obj)
        
    logger.info("Loading done. {0} genes loaded".format(nr_genes))
    logger.info("Time to load genes: {0}".format(datetime.now() - start_time))
