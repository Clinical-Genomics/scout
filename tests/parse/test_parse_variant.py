# -*- coding: utf-8 -*-
import pytest

from scout.exceptions import VcfError
from scout.parse.variant import parse_variant
from scout.parse.variant.variant import get_decoded_str, set_str_info, set_str_source


def test_parse_old_obs_archive_SV(case_obj, cyvcf2_variant):
    """Test parsing local_obs_old and local_obs_old_freq off a variant VCF file"""

    nr_old_obs = 22
    freq_old_obs = 0.3

    # GIVEN a VCF variant containing old local observations stats
    cyvcf2_variant.INFO["clinical_genomics_loqusObs"] = nr_old_obs
    cyvcf2_variant.INFO["clinical_genomics_loqusFrq"] = freq_old_obs

    # WHEN parsing the variant
    parsed_var = parse_variant(cyvcf2_variant, case_obj)

    # THEN the parsed variant should contain these values
    assert parsed_var["local_obs_old"] == nr_old_obs
    assert parsed_var["local_obs_old_freq"] == freq_old_obs


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
    csq_header = "ALLELE|CONSEQUENCE|REVEL_rankscore|REVEL_score"
    csq_entry = "C|missense_variant|0.75|0.22,C|missense_variant|0.75|0.22"  # mimic a variant with transcripts

    cyvcf2_variant.INFO["CSQ"] = csq_entry

    header = [word.upper() for word in csq_header.split("|")]

    # WHEN the variant is parsed
    parsed_variant = parse_variant(variant=cyvcf2_variant, case=case_obj, vep_header=header)

    # THEN the REVEL score should be parsed correctly
    assert parsed_variant["revel_score"] == 0.75
    assert parsed_variant["revel"] == 0.22


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


@pytest.mark.parametrize(
    "header, info",
    [
        (
            '##INFO=<ID=PathologicStruc,Number=1,Type=String,Description="Struc components">',
            "PathologicStruc=[0, 1, 2, 6]",
        ),
        (
            '##INFO=<ID=PathologicStruc,Number=.,Type=Integer,Description="Struc components">',
            "PathologicStruc=0,1,2,6",
        ),
    ],
)
def test_set_str_info_pathologic_struc(str_vcf_variant, header, info):
    """Test that str_pathologic_struc is stored the same way for the old and the new format"""

    # GIVEN an STR variant with a PathologicStruc in the old String or new Integer format
    variant = str_vcf_variant([header], info)
    parsed_variant = {"category": "str"}

    # WHEN setting STR info
    set_str_info(variant, parsed_variant)

    # THEN the PathologicStruc is stored as a list string
    assert parsed_variant["str_pathologic_struc"] == "[0, 1, 2, 6]"


def test_set_str_info_pathologic_struc_single_index_zero(str_vcf_variant):
    """Test that a single new format index 0 is stored, and not dropped as falsy"""

    # GIVEN a new format PathologicStruc with only index 0
    variant = str_vcf_variant(
        ['##INFO=<ID=PathologicStruc,Number=.,Type=Integer,Description="Struc components">'],
        "PathologicStruc=0",
    )
    parsed_variant = {"category": "str"}

    # WHEN setting STR info
    set_str_info(variant, parsed_variant)

    # THEN it is stored as a list string
    assert parsed_variant["str_pathologic_struc"] == "[0]"


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, None),
        ("AD", "AD"),
        ("GeneReviews%20Internet%202019-11-07", "GeneReviews Internet 2019-11-07"),
        ("Paucar%2C%20Nilsson%2C%20Engvall%20et%20al", "Paucar, Nilsson, Engvall et al"),
        ("a%3Bb%3Dc%25d", "a;b=c%d"),
        ("%2c", ","),
        ("%C3%A9", "\u00e9"),
        ("100%", "100%"),
        ("%2", "%2"),
        ("%zz", "%zz"),
    ],
)
def test_get_decoded_str(value, expected):
    """Test percent-decoding of INFO values, keeping plain values and invalid escapes"""
    assert get_decoded_str(value) == expected


def test_set_str_info_percent_encoded_catalog_fields(str_vcf_variant):
    """Test that percent-encoded stranger catalog annotations are decoded"""

    # GIVEN an STR variant with percent-encoded catalog annotations, as written by stranger#124
    variant = str_vcf_variant(
        [
            '##INFO=<ID=Disease,Number=1,Type=String,Description="Disease">',
            '##INFO=<ID=InheritanceMode,Number=.,Type=String,Description="Inheritance mode">',
            '##INFO=<ID=DisplayRU,Number=1,Type=String,Description="Display repeat unit">',
            '##INFO=<ID=SourceDisplay,Number=1,Type=String,Description="Source display">',
            '##INFO=<ID=Source,Number=1,Type=String,Description="Source">',
            '##INFO=<ID=SourceId,Number=1,Type=String,Description="Source id">',
        ],
        "Disease=Spinocerebellar%20ataxia%2C%20type%201;"
        "InheritanceMode=AD,AR;"
        "DisplayRU=CAG;"
        "SourceDisplay=GeneReviews%20Internet%202019-11-07;"
        "Source=GeneReviews;"
        "SourceId=NBK1184",
    )
    parsed_variant = {"category": "str"}

    # WHEN setting STR info and source
    set_str_info(variant, parsed_variant)
    set_str_source(parsed_variant, variant)

    # THEN the values are decoded
    assert parsed_variant["str_disease"] == "Spinocerebellar ataxia, type 1"
    assert parsed_variant["str_inheritance_mode"] == "AD,AR"
    assert parsed_variant["str_display_ru"] == "CAG"
    assert parsed_variant["str_source"] == {
        "display": "GeneReviews Internet 2019-11-07",
        "type": "GeneReviews",
        "id": "NBK1184",
    }
