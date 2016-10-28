from scout.parse.hpo import (parse_hpo_genes, parse_hpo_gene)

def test_parse_hpo_gene_line(hpo_genes_handle):
    header = hpo_genes_handle.next()
    first_gene = hpo_genes_handle.next()

    gene_info = parse_hpo_gene(first_gene)

    assert gene_info['hgnc_symbol'] == first_gene.split('\t')[1]

def test_parse_hpo_genes(hpo_genes_handle):
    header = hpo_genes_handle.next()

    genes = parse_hpo_genes(hpo_genes_handle)
    for hgnc_symbol in genes:
        assert genes[hgnc_symbol]['hgnc_symbol']