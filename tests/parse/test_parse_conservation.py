from scout.parse.variant.conservation import (
    parse_conservations,
    parse_conservation_info,
    parse_conservation_csq,
)


def test_parse_conservation(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with some GERP information
    variant.INFO["dbNSFP_GERP___RS"] = 3.7
    ## WHEN parsing conservation
    ## THEN assert that the field is parsed correct
    assert parse_conservation_info(variant, "dbNSFP_GERP___RS", "gerp") == ["Conserved"]


def test_parse_conservation_multiple_terms(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple GERP annotations
    variant.INFO["dbNSFP_GERP___RS"] = 3.7, -0.34

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned
    assert parse_conservation_info(variant, "dbNSFP_GERP___RS", "gerp") == [
        "Conserved",
        "NotConserved",
    ]


def test_parse_conservations(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple conservation annotations
    variant.INFO["dbNSFP_GERP___RS"] = 4.6, 0
    variant.INFO["dbNSFP_phastCons100way_vertebrate"] = 0.8
    variant.INFO["dbNSFP_phyloP100way_vertebrate"] = 2.4

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned

    conservations = parse_conservations(variant)

    assert conservations["gerp"] == ["Conserved", "NotConserved"]
    assert conservations["phast"] == ["Conserved"]
    assert conservations["phylop"] == ["NotConserved"]


def test_parse_conservation_csq(transcript_info):

    ## GIVEN a trascript with multiple conservation annotations
    keys = ["gerp", "phast", "phylop"]
    csq_entry = """0&4.6|0.8|2.4,0&4.6|0.8|2.4"""
    csq_header = """GERP++_RS|phastCons100way_vertebrate|phyloP100way_vertebrate"""

    transcript_info["gerp"] = "0&4.6"
    transcript_info["phast"] = "0.8"
    transcript_info["phylop"] = "2.4"

    for key in keys:
        conservations = parse_conservation_csq(transcript_info, key)
        assert len(conservations) > 0
        for item in conservations:
            assert item in ["NotConserved", "Conserved"]
