from scout.parse.hpo import (parse_hpo_genes, parse_hpo_gene)

def test_parse_hpo_gene_line(hpo_genes_handle):
    header = next(hpo_genes_handle)
    first_gene = next(hpo_genes_handle)

    gene_info = parse_hpo_gene(first_gene)

    assert gene_info['hgnc_symbol'] == first_gene.split('\t')[1]

def test_parse_hpo_genes(hpo_genes_handle):
    header = next(hpo_genes_handle)

    genes = parse_hpo_genes(hpo_genes_handle)
    for hgnc_symbol in genes:
        assert genes[hgnc_symbol]['hgnc_symbol']