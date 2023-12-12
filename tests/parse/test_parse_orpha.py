from scout.parse.orpha import get_orpha_to_genes_information


def test_get_orpha_to_genes_information(orphadata_en_product6_lines):
    # GIVEN lines from a read file

    # WHEN parsing the tree
    result = get_orpha_to_genes_information(lines=orphadata_en_product6_lines)
    disease = result["ORPHA:585"]

    # THEN assert disease with correct contents was returned
    assert len(result) == 4
    assert disease["description"] == "Multiple sulfatase deficiency"
    assert disease["orpha_code"] == 585
    assert disease["hgnc_ids"] == {"20376"}
