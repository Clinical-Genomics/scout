from scout.parse.hpo_mappings import parse_hpo_to_genes, parse_hpo_diseases


def test_parse_hpo_to_genes(hpo_disease_handle):
    """Test function that parses file phenotype_to_genes.txt and maps phenotypes to genes"""

    # WHEN parsing the phenotype_to_genes.txt file
    hpo_2_genes = parse_hpo_to_genes(hpo_disease_handle)

    # THEN the iterator returned should contain hpo_id and hgnc_symbol
    for item in hpo_2_genes:
        assert item["hpo_id"]
        assert item["hgnc_symbol"]


def test_parse_hpo_diseases(hpo_disease_handle):
    """Test function that extracts disease mapping info from phenotype_to_genes.txt file"""

    # WHEN parsing phenotype_to_genes.txt using the parse_hpo_diseases function
    diseases = parse_hpo_diseases(hpo_disease_handle)

    # THEN the resulting dictionary has OMIM terms as keys
    omim_ids = list(diseases.keys())
    assert omim_ids[0].startswith("OMIM:")

    # and disease info as values
    one_disease = diseases[omim_ids[0]]
    assert one_disease["disease_nr"]
    assert one_disease["hgnc_symbols"]
    assert one_disease["source"] == "OMIM"
