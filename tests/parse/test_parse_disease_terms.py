from scout.parse.disease_terms import (
    combine_disease_information,
    get_all_disease_terms,
    get_omim_disease_terms,
    get_orpha_disease_terms,
    parse_disease_terms,
)


#: TODO: Add running of tests without lines
def test_get_orpha_disease_terms(orphadata_en_product6_lines, orphadata_en_product4_lines):
    #: GIVEN lines from files containing orpha to genes end orpha to hpo mappings
    #: WHEN combining the information into disease terms
    result = get_orpha_disease_terms(
        orpha_to_genes_lines=orphadata_en_product6_lines,
        orpha_to_hpo_lines=orphadata_en_product4_lines,
    )
    # THEN assert disase includes hpo and gene information
    disease = result["ORPHA:585"]

    # THEN assert disease with correct contents including both hpo and genes is included in return
    assert disease["description"] == "Multiple sulfatase deficiency"
    assert disease["hgnc_ids"] == {"20376"}
    assert disease["hpo_terms"] == {"HP:0000238", "HP:0000252", "HP:0000256", "HP:0000280"}


# def test_get_omim_disease_terms(genemap_handle, hpo_phenotype_annotation_handle):
#     #: GIVEN lines from genemap and hpo mappings
#     #: WHEN combining the information into disease terms
#     result = get_omim_disease_terms(genemap_lines=genemap_handle, hpo_annotation_lines=hpo_phenotype_annotation_handle)
#     # THEN assert disase includes hpo and gene information
#     disease = result["ORPHA:585"]
#
#     # THEN assert disease with correct contents including both hpo and genes is included in return
#     assert disease["description"] == "Multiple sulfatase deficiency"
#     assert disease["hgnc_ids"] == {"20376"}
#     assert disease["hpo_terms"] == {"HP:0000238", "HP:0000252", "HP:0000256", "HP:0000280"}
