from scout.parse.exac import parse_exac_genes, parse_exac_line


def test_parse_exac_line(exac_handle):
    """Test to parse a exac line"""
    header = next(exac_handle).rstrip().split("\t")
    first_gene = next(exac_handle)

    gene_info = parse_exac_line(header=header, line=first_gene)

    assert gene_info["hgnc_symbol"] == first_gene.split("\t")[1]


def test_parse_exac_genes(exac_handle):

    genes = parse_exac_genes(exac_handle)

    for gene in genes:
        assert gene["hgnc_symbol"]
