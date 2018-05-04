from scout.utils.link import link_genes
from pprint import pprint as pp

def test_link_genes(genes37_handle, hgnc_handle, exac_handle, 
                    mim2gene_handle, genemap_handle, hpo_genes_handle):
    """docstring for test_link_genes"""
    genes = link_genes(
        ensembl_lines=genes37_handle, 
        hgnc_lines=hgnc_handle, 
        exac_lines=exac_handle, 
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
    )
    for hgnc_id in genes:
        gene_obj = genes[hgnc_id]
        assert gene_obj['hgnc_symbol']
        assert gene_obj['hgnc_id']
        assert gene_obj['chromosome']
        assert gene_obj['start']
        assert gene_obj['end']

        assert gene_obj['hgnc_symbol'] in gene_obj['previous_symbols']
