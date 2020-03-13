"""Tests for scout server links"""

from scout.server.links import add_gene_links


def test_add_gene_links():
    """Test to add gene links to a gene object"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257}
    build = 37
    # WHEN adding the gene links
    add_gene_links(gene_obj, build)
    # THEN assert some links are added
    assert "hgnc_link" in gene_obj


def test_ucsc_link():
    """Test if ucsc link is correctly added"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257, "ucsc_id": "uc001jwi.4"}
    build = 37
    # WHEN adding the gene links
    add_gene_links(gene_obj, build)
    # THEN assert some links are added
    link = gene_obj.get("ucsc_link")
    assert link is not None
