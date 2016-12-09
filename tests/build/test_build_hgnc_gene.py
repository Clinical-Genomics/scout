from scout.build.hgnc_gene import build_hgnc_gene

def test_build_hgnc_genes(genes):
    # GIVEN a dictionary with hgnc genes
    
    # WHEN building hgnc gene objecs
    for hgnc_symbol in genes:
        gene_info = genes[hgnc_symbol]
        gene_obj = build_hgnc_gene(gene_info)

        # THEN check that the gene models have a hgnc id
        assert gene_obj['hgnc_id']

def test_build_hgnc_gene():
    gene_info = {
        'hgnc_id': 100,
        'hgnc_symbol': 'TEST',
        'ensembl_gene_id': 'ENSTEST',
        'chromosome': '1',
        'start': 1,
        'end': 1000,
    }
    gene_obj = build_hgnc_gene(gene_info)
    
    assert gene_obj.hgnc_id == gene_info['hgnc_id']