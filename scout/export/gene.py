import logging

logger = logging.getLogger(__name__)

def export_genes(adapter):
    """Export all genes from the database"""
    logger.info("Exporting all genes to .bed format")
    
    for gene in adapter.all_genes():
        gene_string = ("{0}\t{1}\t{2}\t{3}\t{4}")
        
        yield gene_string.format(
            gene.chromosome,
            gene.start,
            gene.end,
            gene.hgnc_symbol,
            gene.hgnc_id
        )
    