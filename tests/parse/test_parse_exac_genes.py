from scout.parse.exac import parse_constraint_genes, parse_constraint_line


def test_parse_constraint_line(exac_handle):
    """Test parsing a GnomAD constraint line"""
    header = next(exac_handle).rstrip().split("\t")

    for gene in exac_handle:
        # look at the first gene with mane
        gene_with_mane_info = parse_constraint_line(header=header, line=gene)
        if gene_with_mane_info:
            break

    assert gene_with_mane_info["hgnc_symbol"] == gene.split("\t")[0]


def test_parse_constraint_genes(exac_handle):
    """Test parsing the gene constraint"""
    genes = parse_constraint_genes(exac_handle)

    for gene in genes:
        assert gene["hgnc_symbol"]
