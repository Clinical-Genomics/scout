from scout.parse.hgnc import parse_hgnc_line, parse_hgnc_genes


def test_parse_hgnc_line(hgnc_handle):
    """Test to parse a hgnc gene line"""
    header = next(hgnc_handle).split("\t")
    first_gene = next(hgnc_handle)
    gene_info = parse_hgnc_line(header=header, line=first_gene)
    assert gene_info["hgnc_id"] == int(first_gene.split("\t")[0].split(":")[1])


def test_parse_hgnc_genes(hgnc_handle):
    """Test to parse the hgnc genes"""
    genes = parse_hgnc_genes(lines=hgnc_handle)
    for gene in genes:
        if gene:
            assert gene["hgnc_id"]
