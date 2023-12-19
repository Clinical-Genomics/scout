import pytest

from scout.parse.disease_terms import (
    consolidate_gene_and_hpo_annotation,
    get_all_disease_terms,
    get_omim_disease_terms,
    get_orpha_disease_terms,
    parse_disease_terms,
)


def test_get_all_disease_terms(
    orphadata_en_product6_lines,
    orphadata_en_product4_lines,
    genemap_handle,
    hpo_phenotype_annotation_handle,
    test_orpha_disease_terms,
    test_omim_disease_terms,
):
    #: GIVEN lines from the disease sourcefiles
    #: WHEN the disease are compiled
    result: Dict[str, dict] = get_all_disease_terms(
        hpo_annotation_lines=hpo_phenotype_annotation_handle,
        genemap_lines=genemap_handle,
        orpha_to_genes_lines=orphadata_en_product6_lines,
        orpha_to_hpo_lines=orphadata_en_product4_lines,
    )
    #: THEN assert correct contents are present
    for key in test_omim_disease_terms:
        assert key in result
        assert test_omim_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_omim_disease_terms[key]["hgnc_symbols"].issubset(result[key]["hgnc_symbols"])
        assert test_omim_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])
    for key in test_orpha_disease_terms:
        assert key in result
        assert test_orpha_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_orpha_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])


def test_parse_disease_terms(test_omim_disease_terms, test_orpha_disease_terms):
    #: GIVEN a Dict of ORPHA and OMIM disease with gene and hpo information
    #: WHEN the terms are combined
    result: Dict[str, dict] = parse_disease_terms(
        omim_disease_terms=test_omim_disease_terms, orpha_disease_terms=test_orpha_disease_terms
    )
    #: THEN assert the information from both sources are retained
    for key in test_omim_disease_terms:
        assert key in result
        assert test_omim_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_omim_disease_terms[key]["hgnc_symbols"].issubset(result[key]["hgnc_symbols"])
        assert test_omim_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])
    for key in test_orpha_disease_terms:
        assert key in result
        assert test_orpha_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_orpha_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])


@pytest.mark.parametrize(
    "hpo_annotation_fixture_name, gene_annotation_fixture_name",
    [
        ("test_orpha_hpo_annotations", "test_orpha_diseases"),
        ("test_parsed_hpo_annotations", "test_genemap_diseases"),
    ],
)
def test_consolidate_gene_and_hpo_annotation(
    hpo_annotation_fixture_name, gene_annotation_fixture_name, request
):
    #: GIVEN disease annotated with genes and disease annotated with genes
    hpo_annotations = request.getfixturevalue(hpo_annotation_fixture_name)
    gene_annotations = request.getfixturevalue(gene_annotation_fixture_name)
    #: WHEN combining this information
    result = consolidate_gene_and_hpo_annotation(
        hpo_annotations=hpo_annotations, gene_annotations=gene_annotations
    )
    #: THEN assert all original diseases are present and contains gene and hpo information from the original source
    for key in hpo_annotations:
        assert key in result
        assert hpo_annotations[key]["hpo_terms"] == result[key]["hpo_terms"]
    for key in gene_annotations:
        assert key in result
        assert gene_annotations[key]["hgnc_symbols"] == result[key]["hgnc_symbols"]
        assert gene_annotations[key]["hgnc_ids"] == result[key]["hgnc_ids"]


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


def test_get_omim_disease_terms(genemap_handle, hpo_phenotype_annotation_handle):
    #: GIVEN lines from genemap and hpo mappings
    #: WHEN combining the information into disease terms
    result = get_omim_disease_terms(
        genemap_lines=genemap_handle, hpo_annotation_lines=hpo_phenotype_annotation_handle
    )
    # THEN assert disase includes hpo and gene information
    disease = result["OMIM:614116"]

    # THEN assert disease with correct contents including both hpo and genes is included in return
    assert disease["description"] == "Neuropathy hereditary sensory type IE"
    assert disease["hgnc_ids"] == set()
    assert disease["hpo_terms"] == {
        "HP:0000006",
        "HP:0000365",
        "HP:0100710",
        "HP:0000737",
        "HP:0011462",
        "HP:0002460",
        "HP:0000726",
        "HP:0001262",
        "HP:0002354",
        "HP:0002059",
        "HP:0003676",
        "HP:0000407",
        "HP:0001265",
        "HP:0001251",
        "HP:0000741",
    }
