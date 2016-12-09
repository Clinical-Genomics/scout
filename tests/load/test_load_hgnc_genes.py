from scout.load.hgnc_gene import load_hgnc_genes

def test_load_hgnc_genes(adapter, genes):
    # GIVEN a empty database
    assert adapter.all_genes().count() == 0
    
    # WHEN inserting a number of genes
    load_hgnc_genes(adapter, genes)
    
    nr_genes = 0
    for gene_symbol in genes:
        nr_genes += 1
        gene_info = genes[gene_symbol]
    
    # THEN assert all genes have been added to the database
    
    assert adapter.all_genes().count() == nr_genes
    
    assert adapter.hgnc_gene(gene_info['hgnc_id'])