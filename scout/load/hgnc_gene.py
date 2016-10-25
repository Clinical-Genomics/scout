# -*- coding: utf-8 -*-
import logging

from scout.utils.link import link_genes
from scout.build import build_hgnc_gene

logger = logging.getLogger(__name__)


def load_hgnc_genes(adapter, ensembl_transcripts, hgnc_genes, exac_genes, hpo_lines):
    """Load genes with transcripts into the database

        Args:
            adapter(MongoAdapter)
            ensembl_genes(iterable(str))
            hgnc_genes(iterable(str))
            exac_genes(iterable(str))
            hpo_lines(iterable(str))
    """
    genes = link_genes(
        ensembl_transcripts=ensembl_transcripts,
        hgnc_genes=hgnc_genes,
        exac_genes=exac_genes,
        hpo_lines=hpo_lines,
    )
    logger.info("Loading the genes and transcripts...")

    for hgnc_symbol in genes:
        gene = genes[hgnc_symbol]
        gene_obj = build_hgnc_gene(gene)
        adapter.load_hgnc_gene(gene_obj)
    logger.info("Loading done...")
