"""Tests for scout server links"""

from scout.server.links import add_gene_links, cbioportal, mycancergenome


def test_add_gene_links():
    """Test to add gene links to a gene object"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257}
    build = 37
    # WHEN adding the gene links
    add_gene_links(gene_obj, build)
    # THEN assert some links are added
    assert "hgnc_link" in gene_obj


def test_add_hg38_gene_links():
    """Test to add hg38 gene links to a gene object"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257}
    build = 38
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


def test_cbioportal_link():
    """Test if CBioPortal link is made correctly"""

    hgnc_symbol = "TP53"
    protein_change = "p.Ser241Phe"

    link = cbioportal(hgnc_symbol, protein_change)
    assert link is not None


def test_mycancergenome_link():
    hgnc_symbol = "TP53"
    protein_change = "p.Ser241Phe"

    link = mycancergenome(hgnc_symbol, protein_change)
    assert link is not None
