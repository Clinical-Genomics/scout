# -*- coding: utf-8 -*-
from scout.parse.variant import parse_variant
from scout.exceptions import VcfError


def test_parse_minimal(one_variant, case_obj):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(one_variant, case_obj, variant_type='clinical')
    assert parsed_variant['position'] == int(one_variant.POS)
    assert parsed_variant['category'] == 'snv'


def test_parse_with_header(one_variant, case_obj, rank_results_header):
    """docstring for test_parse_all_variants"""
    parsed_variant = parse_variant(one_variant, case_obj,
                                   rank_results_header=rank_results_header)

    assert parsed_variant['chromosome'] == '1'
    assert parsed_variant['rank_result']['Consequence'] == 1


def test_parse_small_sv(one_sv_variant, case_obj):
    parsed_variant = parse_variant(one_sv_variant, case_obj)

    assert parsed_variant['category'] == 'sv'
    assert parsed_variant['sub_category'] == one_sv_variant.INFO['SVTYPE'].lower()
    assert parsed_variant['position'] == int(one_sv_variant.POS)


def test_parse_many_snvs(variants, case_obj):
    """docstring for test_parse_all_variants"""

    for variant in variants:
        parsed_variant = parse_variant(variant, case_obj)
        assert parsed_variant['chromosome'] == variant.CHROM


def test_parse_many_svs(sv_variants, case_obj):
    """docstring for test_parse_all_variants"""

    for variant in sv_variants:
        try:
            parsed_variant = parse_variant(variant, case_obj)
        except VcfError:
            for info in variant['info_dict']:
                print(info, variant['info'])
            assert False
        assert parsed_variant['chromosome'] == variant.CHROM


def test_parse_cadd(variants, case_obj):
    # GIVEN some parsed variant dicts
    for variant in variants:
        # WHEN score is present
        if 'CADD' in variant.INFO:
            cadd_score = float(variant.INFO['CADD'])
            parsed_variant = parse_variant(variant, case_obj)
            # THEN make sure that the cadd score is parsed correct
            assert parsed_variant['cadd_score'] == cadd_score
