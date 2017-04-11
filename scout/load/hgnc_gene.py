# -*- coding: utf-8 -*-
import logging

from datetime import datetime

from scout.build import build_hgnc_gene

logger = logging.getLogger(__name__)


def load_hgnc_genes(adapter, genes, build='37'):
    """Load genes with transcripts into the database

        Args:
            adapter(MongoAdapter)
            genes(dict): Dictionary with gene symbols as keys and gene
                         info as values
    """
    logger.info("Loading the genes and transcripts, build %s", build)
    start_time = datetime.now()
    non_existing = 0
    nr_genes = 0
    for nr_genes, gene_data in enumerate(genes.values()):
        if not gene_data.get('chromosome'):
            logger.debug("skipping gene: %s", gene_data['hgnc_symbol'])
            non_existing += 1
        else:
            gene_obj = build_hgnc_gene(gene_data, build=build)
            adapter.load_hgnc_gene(gene_obj)

    logger.info("Loading done. {0} genes loaded".format(nr_genes - non_existing))
    logger.info("Time to load genes: {0}".format(datetime.now() - start_time))
    logger.info("Nr of genes without coordinates in build {0}: {1}".format(
                build, non_existing))
