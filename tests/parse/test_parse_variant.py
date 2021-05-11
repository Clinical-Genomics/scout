# -*- coding: utf-8 -*-
from scout.exceptions import VcfError
from scout.parse.variant import parse_variant


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


def test_parse_mitomapassociateddiseases(cyvcf2_variant, case_obj):
    """Test parsing HmtVar value from variant annotated with HmtNote"""

    # GIVEN a variant containing HmtVar key in the INFO field:
    cyvcf2_variant.INFO["MitomapAssociatedDiseases"] = "LHON"

    # THEN make sure that it is parsed correctly
    mitomap_associated_diseases = cyvcf2_variant.INFO["MitomapAssociatedDiseases"]
    parsed_variant = parse_variant(cyvcf2_variant, case_obj)
    assert parsed_variant["mitomap_associated_diseases"] == mitomap_associated_diseases


def test_parse_hmtvar(cyvcf2_variant, case_obj):
    """Test parsing HmtVar value from variant annotated with HmtNote"""

    # GIVEN a variant containing HmtVar key in the INFO field:
    cyvcf2_variant.INFO["HmtVar"] = "39192"

    # THEN make sure that it is parsed correctly
    hmtvar_variant_id = int(cyvcf2_variant.INFO["HmtVar"])
    parsed_variant = parse_variant(cyvcf2_variant, case_obj)
    assert parsed_variant["hmtvar_variant_id"] == hmtvar_variant_id
