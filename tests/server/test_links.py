"""Tests for scout server links"""

import responses
from flask import url_for

from scout.server.links import (
    add_gene_links,
    alamut_link,
    cbioportal,
    marrvel_link,
    mycancergenome,
    snp_links,
)


def test_marrvel_link_build_37(variant_obj):
    """Test creating a MARRVEL link for a variant in build 37"""
    # GIVEN a variant object of genome build 37:
    m_link = marrvel_link(variant_obj, 37)
    # THEN the Marrvel link should contain the original variant coordinates
    assert (
        m_link
        == f"http://marrvel.org/human/variant/{variant_obj['chromosome']}:{variant_obj['position']} {variant_obj['reference']}>{variant_obj['alternative']}"
    )


@responses.activate
def test_marrvel_link_build_38():
    """Test creating a MARRVEL link for a variant in build 38"""
    # GIVEN a variant in genome build 38:
    variant_obj_38 = {"chromosome": "X", "position": 1039265, "reference": "T", "alternative": "C"}

    # THAT can be lifted over to build 37:
    url = f"http://grch37.rest.ensembl.org/map/human/GRCh38/{variant_obj_38['chromosome']}:{variant_obj_38['position']}..{variant_obj_38['position']}/GRCh37?content-type=application/json"

    liftover_mappings = {
        "mappings": [
            {
                "original": {
                    "assembly": "GRCh38",
                    "seq_region_name": variant_obj_38["chromosome"],
                    "start": variant_obj_38["position"],
                    "end": variant_obj_38["position"] + 100,
                },
                "mapped": {
                    "assembly": "GRCh37",
                    "seq_region_name": variant_obj_38["chromosome"],
                    "start": 1000000,
                    "end": 1000100,
                },
            }
        ]
    }
    responses.add(
        responses.GET,
        url,
        json=liftover_mappings,
        status=200,
    )
    # WHEN MARRVEL link is created
    m_link = marrvel_link(variant_obj_38, 38)
    # THEN it should contain the variant in build 37 coordinates
    assert (
        m_link
        == f'http://marrvel.org/human/variant/{liftover_mappings["mappings"][0]["mapped"]["seq_region_name"]}:{liftover_mappings["mappings"][0]["mapped"]["start"]} T>C'
    )


def test_alamut_link(app, institute_obj, variant_obj):
    """Test to add a link to alamut browser"""

    # GIVEN an institute with settings for Alamut Visual Plus
    alamut_api_key = "test_alamut_key"
    institute_obj["alamut_key"] = alamut_api_key

    # GIVEN that genome build 38 is provided
    build = 38

    # GIVEN that the app settings contain parameter HIDE_ALAMUT_LINK = False
    app.config["HIDE_ALAMUT_LINK"] = False

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the alamut link is created
        link_to_alamut = alamut_link(institute_obj, variant_obj, 38)
        # THEN the link should contain genome build info
        assert "GRCh38" in link_to_alamut
        # As well as Alamut Visual Plus API key
        assert alamut_api_key in link_to_alamut


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
