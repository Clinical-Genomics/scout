# -*- coding: utf-8 -*-
from scout.parse.variant import parse_variant
from scout.exceptions import VcfError


def test_parse_minimal(one_variant, case_obj):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(one_variant, case_obj, variant_type="clinical")
    assert parsed_variant["position"] == int(one_variant.POS)
    assert parsed_variant["category"] == "snv"


def test_parse_with_header(one_variant, case_obj, rank_results_header):
    """docstring for test_parse_all_variants"""
    parsed_variant = parse_variant(one_variant, case_obj, rank_results_header=rank_results_header)

    assert parsed_variant["chromosome"] == "1"
    assert parsed_variant["rank_result"]["Consequence"] == 1


def test_parse_small_sv(one_sv_variant, case_obj):
    parsed_variant = parse_variant(one_sv_variant, case_obj)

    assert parsed_variant["category"] == "sv"
    assert parsed_variant["sub_category"] == one_sv_variant.INFO["SVTYPE"].lower()
    assert parsed_variant["position"] == int(one_sv_variant.POS)


def test_parse_small_str(one_str_variant, case_obj):
    parsed_variant = parse_variant(one_str_variant, case_obj, category="str")

    assert parsed_variant["category"] == "str"
    assert parsed_variant["str_status"] == one_str_variant.INFO["STR_STATUS"]
    assert parsed_variant["str_normal_max"] == one_str_variant.INFO["STR_NORMAL_MAX"]
    assert parsed_variant["str_pathologic_min"] == one_str_variant.INFO["STR_PATHOLOGIC_MIN"]
    assert parsed_variant["position"] == int(one_str_variant.POS)


def test_parse_many_snvs(variants, case_obj):
    """docstring for test_parse_all_variants"""

    for variant in variants:
        parsed_variant = parse_variant(variant, case_obj)
        assert parsed_variant["chromosome"] == variant.CHROM


def test_parse_many_svs(sv_variants, case_obj):
    """docstring for test_parse_all_variants"""

    for variant in sv_variants:
        try:
            parsed_variant = parse_variant(variant, case_obj)
        except VcfError:
            for info in variant["info_dict"]:
                print(info, variant["info"])
            assert False
        assert parsed_variant["chromosome"] == variant.CHROM


def test_parse_many_strs(str_variants, case_obj):
    """docstring for test_parse_many_strs"""

    for variant in str_variants:
        try:
            parsed_variant = parse_variant(variant, case_obj, category="str")
        except VcfError:
            for info in variant["info_dict"]:
                print(info, variant["info"])
            assert False
        assert parsed_variant["chromosome"] == variant.CHROM


def test_parse_cadd(variants, case_obj):
    # GIVEN some parsed variant dicts
    for variant in variants:
        # WHEN score is present
        if "CADD" in variant.INFO:
            cadd_score = float(variant.INFO["CADD"])
            parsed_variant = parse_variant(variant, case_obj)
            # THEN make sure that the cadd score is parsed correct
            assert parsed_variant["cadd_score"] == cadd_score


def test_parse_spliceai(cyvcf2_variant, case_obj):
    """Test parse Splice AI
    Two variant INFO fields are imported:
        SpliceAI_DS_Max(float)
        SpliceAI(str):
            SpliceAIv1.3 variant annotation.
            These include delta scores (DS) and delta positions (DP) for acceptor gain (AG),
            acceptor loss (AL), donor gain (DG), and donor loss (DL).
            Format: ALLELE|SYMBOL|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL
    """
    # GIVEN a variant with expected info fields
    spliceai_ds_max = 0.91
    cyvcf2_variant.INFO["SpliceAI_DS_Max"] = spliceai_ds_max
    spliceai = "G|PLK3|0.00|0.00|0.91|0.53|-1|-14|-1|2"
    cyvcf2_variant.INFO["SpliceAI"] = spliceai

    # WHEN parsing variant
    parsed_variant = parse_variant(cyvcf2_variant, case_obj)

    # THEN make sure that the spliceai entries have been parsed correctly
    assert parsed_variant["spliceai_ds_max"] == spliceai_ds_max
    assert parsed_variant["spliceai"] == spliceai


def test_parse_revel(cyvcf2_variant, case_obj):
    ## GIVEN a variant with REVEL score in the CSQ entry
    csq_header = "ALLELE|CONSEQUENCE|REVEL_rankscore"
    csq_entry = (
        "C|missense_variant|0.75,C|missense_variant|0.75"  # mimic a variant with transcripts
    )

    cyvcf2_variant.INFO["CSQ"] = csq_entry

    header = [word.upper() for word in csq_header.split("|")]

    # WHEN the variant is parsed
    parsed_variant = parse_variant(variant=cyvcf2_variant, case=case_obj, vep_header=header)

    # THEN the REVEL score should be parsed correctly
    assert parsed_variant["revel_score"] == 0.75


def test_parse_customannotation(one_variant_customannotation, case_obj):
    """Test parsing of custom annotations"""
    parsed_variant = parse_variant(one_variant_customannotation, case_obj)
    assert parsed_variant["custom"] == [["key1", "val1"], ["key2", "val2"]]
