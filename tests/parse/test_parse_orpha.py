from typing import List
from xml.etree.ElementTree import Element

from scout.parse.orpha import (
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


def test_get_orpha_to_genes_information(orpha_to_genes_lines: List[str]):
    """Test the extraction of disease related genes from orphadata file contents"""
    # GIVEN lines from a read file
    # WHEN extracting the orpha to gene information
    result = get_orpha_to_genes_information(lines=orpha_to_genes_lines)
    disease: dict = result["ORPHA:585"]

    # THEN assert disease with correct contents was included in the return

    assert disease["description"] == "Multiple sulfatase deficiency"
    assert disease["hgnc_ids"] == {20376}


def test_get_orpha_to_hpo_information(orpha_to_hpo_lines: List[str]):
    """Test the extraction of disease related hpo-terms from orphadata file contents"""
    # GIVEN lines from a read file
    # WHEN parsing the tree
    result = get_orpha_to_hpo_information(lines=orpha_to_hpo_lines)
    disease = result["ORPHA:58"]

    # THEN assert disease with correct contents was included in return
    assert disease["description"] == "Alexander disease"
    assert disease["hpo_terms"] == {"HP:0000256", "HP:0001249", "HP:0001288", "HP:0001337"}
