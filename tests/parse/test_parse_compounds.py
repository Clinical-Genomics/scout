# -*- coding: utf-8 -*-
from scout.parse.variant.compound import parse_compounds


def test_parse_simple_compound(case_obj):
    ## GIVEN a compound string
    compound_string = "internal_id:7_117175579_AT_A>32"

    ## When parsing the compounds
    compounds = parse_compounds(compound_string, case_id=case_obj["_id"], variant_type="clinical")
    compound = compounds[0]

    ## THEN assert that the correct info is returned
    assert compound["display_name"] == "7_117175579_AT_A"
    assert compound["score"] == 32.0


def test_parse_compound_no_score(case_obj):
    ## GIVEN a compound string
    compound_string = "internal_id:7_117175579_AT_A"

    ## When parsing the compounds
    compounds = parse_compounds(compound_string, case_id=case_obj["_id"], variant_type="clinical")
    compound = compounds[0]

    ## THEN assert that the correct info is returned
    assert compound["display_name"] == "7_117175579_AT_A"
    assert compound["score"] == 0.0


def test_parse_compound_no_compound(case_obj):
    ## GIVEN a compound string
    compound_string = None

    ## When parsing the compounds
    compounds = parse_compounds(compound_string, case_id=case_obj["_id"], variant_type="clinical")

    ## THEN assert that the correct info is returned
    assert compounds == []


def test_parse_multiple_compound(case_obj):
    ## GIVEN a compound string
    compound_string = "internal_id:7_117175579_AT_A>32|7_117175580_T_G>28"

    ## When parsing the compounds
    compounds = parse_compounds(compound_string, case_id=case_obj["_id"], variant_type="clinical")

    ## THEN assert that the correct info is returned
    assert len(compounds) == 2
