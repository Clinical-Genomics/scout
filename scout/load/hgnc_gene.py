from scout.utils import link_genes
from scout.build import build_hgnc_gene

from pprint import pprint as pp

def load_hgnc_genes(adapter, ensembl_transcripts, hgnc_genes, exac_genes):
    """Load genes with transcripts into the database
    
        Args:
            adapter(MongoAdapter)
            ensembl_genes(iterable(str))
            hgnc_genes(iterable(str))
            exac_genes(iterable(str))
    """
    genes = link_genes(
        ensembl_transcripts=ensembl_transcripts,
        hgnc_genes=hgnc_genes, 
        exac_genes=exac_genes
    )

    for hgnc_symbol in genes:
        gene = genes[hgnc_symbol]
        gene_obj = build_hgnc_gene(gene)
        pp(gene_obj.to_json())
    
    