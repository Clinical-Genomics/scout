from scout.parse.exac import parse_constraint_genes, parse_constraint_line


def test_parse_constraint_line(exac_handle):
    """Test parsing a GnomAD constraint line"""
    header = next(exac_handle).rstrip().split("\t")
    first_gene = next(exac_handle)

    gene_info = parse_constraint_line(header=header, line=first_gene)

    assert gene_info["hgnc_symbol"] == first_gene.split("\t")[0]


def test_parse_constraint_genes(exac_handle):
    """Test parsing the gene constraint"""
    genes = parse_constraint_genes(exac_handle)

    for gene in genes:
        assert gene["hgnc_symbol"]
