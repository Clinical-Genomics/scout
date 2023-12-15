"""Tests for scout server links"""

from flask import url_for

from scout.server.links import (
    BEACON_LINK_TEMPLATE,
    add_gene_links,
    alamut_gene_link,
    alamut_variant_link,
    beacon_link,
    cbioportal,
    ckb_gene,
    mutalyzer,
    mycancergenome,
    snp_links,
)

BUILD_37 = 37
BUILD_38 = 38

BEACON_BUILD_37 = "GRCh37"
BEACON_BUILD_38 = "GRCh38"


def test_beacon_link_37(variant_obj):
    """Test building a beacon link for a variant in build 37"""
    # GIVEN a variant in genome build 37
    build = BUILD_37

    # THEN the Beacon link should reflect the variant build
    expected_link = BEACON_LINK_TEMPLATE.format(this=variant_obj, build=BEACON_BUILD_37)
    link = beacon_link(variant_obj, build)
    assert expected_link == link


def test_beacon_link_38(variant_obj):
    """Test building a beacon link for a variant in build 38"""

    # GIVEN a variant in genome build 38
    build = BUILD_38

    # THEN the Beacon link should reflect the variant build
    expected_link = BEACON_LINK_TEMPLATE.format(this=variant_obj, build=BEACON_BUILD_38)
    link = beacon_link(variant_obj, build)
    assert expected_link == link


def test_alamut_link_build38(app, institute_obj, variant_obj):
    """Test to add a link to alamut browser"""

    # GIVEN an institute with settings for Alamut Visual Plus
    alamut_api_key = "test_alamut_key"
    alamut_api_institute = "test_institute"
    institute_obj["alamut_key"] = alamut_api_key
    institute_obj["alamut_institution"] = alamut_api_institute

    # GIVEN that the app settings contain parameter HIDE_ALAMUT_LINK = False
    app.config["HIDE_ALAMUT_LINK"] = False

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the alamut link is created
        link_to_alamut = alamut_variant_link(institute_obj, variant_obj, BUILD_38)
        # THEN the link should contain genome build info
        assert "GRCh38" in link_to_alamut
        # As well as Alamut Visual Plus API key and institution
        assert alamut_api_key in link_to_alamut
        assert alamut_api_institute in link_to_alamut


def test_alamut_gene_link(app, institute_obj):
    """Test to add a link to alamut browser"""
    gene_obj = {
        "hgnc_id": 257,
        "canonical_transcript": "NM_00545352.3",
        "hgvs_identifier": "c.523dup",
    }
    # GIVEN an institute with settings for Alamut Visual Plus
    alamut_api_key = "test_alamut_key"
    alamut_api_institute = "test_institute"
    institute_obj["alamut_key"] = alamut_api_key
    institute_obj["alamut_institution"] = alamut_api_institute

    # GIVEN that the app settings contain parameter HIDE_ALAMUT_LINK = False
    app.config["HIDE_ALAMUT_LINK"] = False

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the alamut link is created
        link_to_alamut = alamut_gene_link(institute_obj, gene_obj, BUILD_38)

        # Asssert key and institution found in link
        assert alamut_api_key in link_to_alamut
        assert alamut_api_institute in link_to_alamut


def test_add_gene_links_build37():
    """Test to add gene links to a gene object"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257}

    # WHEN adding the gene links
    add_gene_links(gene_obj, BUILD_37)
    # THEN assert some links are added
    assert "hgnc_link" in gene_obj


def test_add_gene_links_build38():
    """Test to add hg38 gene links to a gene object"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257}

    # WHEN adding the gene links
    add_gene_links(gene_obj, BUILD_38)
    # THEN assert some links are added
    assert "hgnc_link" in gene_obj


def test_ucsc_link_build37():
    """Test if ucsc link is correctly added"""
    # GIVEN a minimal gene and a genome build
    gene_obj = {"hgnc_id": 257, "ucsc_id": "uc001jwi.4"}

    # WHEN adding the gene links
    add_gene_links(gene_obj, BUILD_37)
    # THEN assert some links are added
    link = gene_obj.get("ucsc_link")
    assert link is not None


def test_mutalyzer_link(app):
    """Test if Mutalyzer link is made correctly"""

    refseq = "NM_001042594"
    hgvs = "c.510G>T"
    link = mutalyzer(refseq, hgvs)
    assert link


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


def test_ckb_link():
    """Test building the link for The Clinical KnowledgeBase (Jackson Lab)"""
    entrez_id = 7015
    link = ckb_gene(entrez_id)
    assert link is not None


def test_snp_links():
    """Test building the links for the SNP ids of a variant"""
    # GIVEN a variant with multiple SNP IDs
    variant_obj = {"dbsnp_id": "rs150429680;431849"}

    links = snp_links(variant_obj)

    # THEN the links should point to the right database
    snp_ids = variant_obj["dbsnp_id"].split(";")
    for snp in snp_ids:
        if "rs" in snp:  # dbSNP
            assert links[snp] == f"https://www.ncbi.nlm.nih.gov/snp/{snp}"
        else:  # ClinVar variation
            assert links[snp] == f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{snp}"
