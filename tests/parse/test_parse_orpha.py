from typing import List
from xml.etree.ElementTree import Element

from scout.parse.orpha import (
    get_orpha_inheritance_information,
    get_orpha_to_genes_information,
    get_orpha_to_hpo_information,
    parse_orpha_downloads,
)


def test_parse_orpha_downloads(orpha_to_genes_lines: List[str]):
    """Test the parsing of orphadata file contents and assert it has the correct type and root element"""
    # GIVEN lines from a read file
    # WHEN parsing the lines into an element tree
    result = parse_orpha_downloads(orpha_to_genes_lines)

    # Then assert its type and root
    assert type(result) is Element
    assert result.tag == "JDBOR"


def test_get_orpha_to_genes_information(orpha_to_genes_lines: List[str], test_orpha_disease_terms):
    """Test the extraction of disease related genes from orphadata file contents"""
    # GIVEN lines from a read file
    # WHEN extracting the orpha to gene information
    result = get_orpha_to_genes_information(lines=orpha_to_genes_lines)

    # THEN assert expected contents was included in return
    for disease in test_orpha_disease_terms:
        assert test_orpha_disease_terms[disease]["hgnc_ids"].issubset(result[disease]["hgnc_ids"])
        assert test_orpha_disease_terms[disease]["description"] == result[disease]["description"]


def test_get_orpha_to_hpo_information(orpha_to_hpo_lines: List[str], test_orpha_disease_terms):
    """Test the extraction of disease related hpo-terms from orphadata file contents"""
    # GIVEN lines from a read file
    # WHEN parsing the tree
    result = get_orpha_to_hpo_information(lines=orpha_to_hpo_lines)

    # THEN assert expected contents was included in return
    for disease in test_orpha_disease_terms:
        assert test_orpha_disease_terms[disease]["hpo_terms"].issubset(result[disease]["hpo_terms"])
        assert test_orpha_disease_terms[disease]["description"] == result[disease]["description"]


def test_get_orpha_inheritance_information(
    orpha_inheritance_lines: List[str], test_orpha_disease_terms
):
    """Test the extraction of disease related hpo-terms from orphadata file contents"""
    # GIVEN lines from a read file
    # WHEN parsing the tree
    result = get_orpha_inheritance_information(lines=orpha_inheritance_lines)

    # THEN assert disease with correct contents was included in return
    for disease in test_orpha_disease_terms:
        assert test_orpha_disease_terms[disease]["inheritance"].issubset(
            result[disease]["inheritance"]
        )
