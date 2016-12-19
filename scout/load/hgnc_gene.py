# -*- coding: utf-8 -*-
import logging

from datetime import datetime

from scout.build import build_hgnc_gene

logger = logging.getLogger(__name__)


def load_hgnc_genes(adapter, genes):
    """Load genes with transcripts into the database

        Args:
            adapter(MongoAdapter)
            genes(dict): Dictionary with gene symbols as keys and gene
                         info as values
    """
    logger.info("Loading the genes and transcripts...")
    start_time = datetime.now()
    non_existing = 0
    for nr_genes, hgnc_symbol in enumerate(genes):
        gene = genes[hgnc_symbol]
        if 'ensembl_gene_id' not in gene:
            non_existing += 1
        else:
            gene_obj = build_hgnc_gene(gene)
            adapter.load_hgnc_gene(gene_obj)

    logger.info("Loading done. {0} genes loaded".format(nr_genes))
    logger.info("Time to load genes: {0}".format(datetime.now() - start_time))
    logger.info("Nr of genes not present in GRCh37:{0}".format(non_existing))
