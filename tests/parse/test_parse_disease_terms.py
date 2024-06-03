from typing import Dict

import pytest

from scout.parse.disease_terms import (
    consolidate_gene_and_hpo_annotation,
    get_all_disease_terms,
    get_omim_disease_terms,
    get_orpha_disease_terms,
    parse_disease_terms,
)


def test_get_all_disease_terms(
    orpha_to_genes_lines,
    orpha_to_hpo_lines,
    orpha_inheritance_lines,
    genemap_handle,
    hpo_phenotype_annotation_handle,
    test_orpha_disease_terms,
    test_omim_disease_terms,
):
    """Tests function for creating a single dict containing disease_terms with hpo and gene annotations from read
    orphadata and omim files"""
    #: GIVEN lines from the disease sourcefiles
    #: WHEN the disease are compiled
    result: Dict[str, dict] = get_all_disease_terms(
        hpo_annotation_lines=hpo_phenotype_annotation_handle,
        genemap_lines=genemap_handle,
        orpha_to_genes_lines=orpha_to_genes_lines,
        orpha_to_hpo_lines=orpha_to_hpo_lines,
        orpha_inheritance_lines=orpha_inheritance_lines,
    )
    #: THEN assert correct contents are present
    for key in test_omim_disease_terms:
        assert key in result
        assert test_omim_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_omim_disease_terms[key]["hgnc_symbols"].issubset(result[key]["hgnc_symbols"])
        assert test_omim_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])
        assert test_omim_disease_terms[key]["inheritance"].issubset(result[key]["inheritance"])
    for key in test_orpha_disease_terms:
        assert key in result
        assert test_orpha_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_orpha_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])
        assert test_orpha_disease_terms[key]["inheritance"].issubset(result[key]["inheritance"])


def test_parse_disease_terms(test_omim_disease_terms, test_orpha_disease_terms):
    """Tests the function combining orpha and omim disease_terms, verifying none of the contents are lost"""
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
        ("test_orpha_hpo_annotations", "test_orpha_gene_annotations"),
        ("test_parsed_hpo_annotations", "test_genemap_diseases"),
    ],
)
def test_consolidate_gene_and_hpo_annotation(
    hpo_annotation_fixture_name, gene_annotation_fixture_name, request
):
    """Tests function combining hpo and gene information into disease_terms"""
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


def test_get_orpha_disease_terms(
    orpha_to_genes_lines, orpha_to_hpo_lines, orpha_inheritance_lines, test_orpha_disease_terms
):
    """Tests function creating orpha disease_terms with gene and hpo annotations"""
    #: GIVEN lines from files containing orpha to genes end orpha to hpo mappings
    #: WHEN combining the information into disease terms
    result = get_orpha_disease_terms(
        orpha_to_genes_lines=orpha_to_genes_lines,
        orpha_to_hpo_lines=orpha_to_hpo_lines,
        orpha_inheritance_lines=orpha_inheritance_lines,
    )
    # # THEN assert disease with correct contents including both hpo and genes is included in return
    for key in test_orpha_disease_terms:
        assert key in result
        assert test_orpha_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_orpha_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])
        assert test_orpha_disease_terms[key]["inheritance"].issubset(result[key]["inheritance"])
        assert test_orpha_disease_terms[key]["description"] == result[key]["description"]


def test_get_omim_disease_terms(
    genemap_handle, hpo_phenotype_annotation_handle, test_omim_disease_terms
):
    """Tests function creating omim and orpha disease_terms with gene and hpo annotations"""
    #: GIVEN lines from genemap and hpo mappings
    #: WHEN combining the information into disease terms
    result = get_omim_disease_terms(
        genemap_lines=genemap_handle, hpo_annotation_lines=hpo_phenotype_annotation_handle
    )

    # THEN assert disease with correct contents including both hpo and genes is included in return
    for key in test_omim_disease_terms:
        assert key in result
        assert test_omim_disease_terms[key]["hpo_terms"].issubset(result[key]["hpo_terms"])
        assert test_omim_disease_terms[key]["hgnc_ids"].issubset(result[key]["hgnc_ids"])
        assert test_omim_disease_terms[key]["description"] == result[key]["description"]
        assert test_omim_disease_terms[key]["inheritance"] == result[key]["inheritance"]
