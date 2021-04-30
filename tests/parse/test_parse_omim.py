from scout.parse.omim import (
    get_mim_phenotypes,
    parse_genemap2,
    parse_genemap2_phenotypes,
    parse_mim2gene,
    parse_mim_titles,
    parse_omim_line,
)


def test_parse_omim_line():
    ## GIVEN a header and a line
    header = ["a", "b", "c"]
    line = "1\t2\t3"
    ## WHEN parsing the omim line
    res = parse_omim_line(line, header)

    ## THEN assert a dict was built by the header and the line
    assert res["a"] == "1"
    assert res["b"] == "2"
    assert res["c"] == "3"


def test_parse_genemap2_phenotype_entry_single():
    # GIVEN a phenotype description with one entry
    entry = "Ehlers-Danlos syndrome, progeroid type," " 2, 615349 (3), Autosomal recessive"
    # WHEN parsing the entry
    parsed_entries = parse_genemap2_phenotypes(entry)
    parsed_entry = parsed_entries[0]
    # THEN assert that the information was parsed correct

    assert parsed_entry["mim_number"] == 615349
    assert parsed_entry["inheritance"] == {"AR"}
    assert parsed_entry["status"] == "established"


def test_parse_genemap(genemap_lines):

    for res in parse_genemap2(genemap_lines):
        assert res["Chromosome"] == "chr1"
        assert res["mim_number"] == 615291
        assert res["hgnc_symbol"] == "B3GALT6"
        assert res["inheritance"] == set(["AR"])
        for phenotype in res["phenotypes"]:
            assert phenotype["mim_number"]
            assert phenotype["inheritance"]


def test_parse_genemap_file(genemap_handle):
    # WHEN parsing a valid genemap handle
    i = 0
    for i, res in enumerate(parse_genemap2(genemap_handle)):
        assert "mim_number" in res
    # THEN items are returned
    assert i > 0


def test_parse_mim2gene(mim2gene_lines):
    ## GIVEN some lines from a mim2gene file
    mim2gene_info = parse_mim2gene(mim2gene_lines)

    ## WHEN parsing the lines
    first_entry = next(mim2gene_info)

    ## ASSERT that they are correctly parsed

    # First entry is a gene so it should have a hgnc symbol
    assert first_entry["mim_number"] == 615291
    assert first_entry["entry_type"] == "gene"
    assert first_entry["hgnc_symbol"] == "B3GALT6"


def test_parse_mim2gene_file(mim2gene_handle):
    i = 0
    # Just check that the file exists and that some result is given
    for i, res in enumerate(parse_mim2gene(mim2gene_handle)):
        assert "mim_number" in res
    assert i > 0


def test_get_mim_phenotypes(genemap_lines):
    ## GIVEN a small testdata set

    # This will return a dictionary with mim number as keys and
    # phenotypes as values

    ## WHEN parsing the phenotypes
    phenotypes = get_mim_phenotypes(genemap_lines=genemap_lines)

    ## THEN assert they where parsed in a correct way

    # There was only one line in genemap_lines that have two phenotypes
    # so we expect that there should be two phenotypes

    assert len(phenotypes) == 2

    term = phenotypes[615349]

    assert term["inheritance"] == set(["AR"])
    assert term["hgnc_symbols"] == set(["B3GALT6"])


def test_get_mim_phenotypes_file(genemap_handle):
    phenotypes = get_mim_phenotypes(genemap_lines=genemap_handle)
    i = 0
    for i, mim_nr in enumerate(phenotypes):
        assert phenotypes[mim_nr]["mim_number"]

    assert i > 0
