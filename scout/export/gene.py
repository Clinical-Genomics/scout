import logging

LOG = logging.getLogger(__name__)


def export_genes(adapter, build="37"):
    """Export all genes from the database"""
    LOG.info("Exporting all genes to .bed format")

    for gene_obj in adapter.all_genes(build=build):
        yield gene_obj
