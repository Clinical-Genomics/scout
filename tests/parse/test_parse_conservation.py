from scout.parse.variant.conservation import (
    parse_conservation_csq,
    parse_conservation_info,
    parse_conservations,
)


def test_parse_conservation(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with some GERP information
    variant.INFO["dbNSFP_GERP___RS"] = 3.7
    ## WHEN parsing conservation
    ## THEN assert that the field is parsed correct
    assert parse_conservation_info(variant, "dbNSFP_GERP___RS", "gerp") == ["Conserved (3.7)"]


def test_parse_conservation_multiple_terms(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple GERP annotations
    variant.INFO["dbNSFP_GERP___RS"] = 3.7, -0.34

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned
    assert parse_conservation_info(variant, "dbNSFP_GERP___RS", "gerp") == [
        "Conserved (3.7)",
        "NotConserved (-0.34)",
    ]


def test_parse_conservations(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple conservation annotations
    variant.INFO["dbNSFP_GERP___RS"] = 4.6, 0
    variant.INFO["dbNSFP_phastCons100way_vertebrate"] = 0.8
    variant.INFO["dbNSFP_phyloP100way_vertebrate"] = 2.4

    ## WHEN parsing conservation
    conservations = parse_conservations(variant)

    ## THEN assert that all terms are returned
    assert conservations["gerp"] == ["Conserved (4.6)", "NotConserved (0)"]
    assert conservations["phast"] == ["Conserved (0.8)"]
    assert conservations["phylop"] == ["NotConserved (2.4)"]


def test_parse_conservation_csq(transcript_info):
    # GIVEN a transcript with multiple conservation annotations
    transcript_info["gerp"] = "0&4.6"
    transcript_info["phast"] = "0.8"
    transcript_info["phylop"] = "2.4"

    # WHEN parsing each conservation key
    gerp_result = parse_conservation_csq(transcript_info, "gerp")
    phast_result = parse_conservation_csq(transcript_info, "phast")
    phylop_result = parse_conservation_csq(transcript_info, "phylop")

    # THEN assert exact output values
    assert gerp_result == ["NotConserved (0.0)", "Conserved (4.6)"]
    assert phast_result == ["Conserved (0.8)"]
    assert phylop_result == ["NotConserved (2.4)"]
