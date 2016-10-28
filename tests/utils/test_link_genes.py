from scout.utils.link import link_genes

def test_link_genes(transcripts_handle, hgnc_handle, exac_handle, hpo_genes_handle):
    """docstring for test_link_genes"""
    genes = link_genes(
        ensembl_lines=transcripts_handle, 
        hgnc_lines=hgnc_handle, 
        exac_lines=hgnc_handle, 
        hpo_lines=hpo_genes_handle
    )
    for hgnc_symbol in genes:
        assert genes[hgnc_symbol]['hgnc_symbol']