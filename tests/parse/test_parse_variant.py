from scout.parse.case import parse_case
from scout.parse.variant import parse_variant
from scout.exceptions import VcfError

def test_parse_minimal(one_variant, parsed_case):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(one_variant, parsed_case, 
                                   variant_type='clinical')
    
    assert parsed_variant['position'] == int(one_variant['POS'])
    assert parsed_variant['category'] == 'snv'

def test_parse_with_header(one_variant, parsed_case, rank_results_header):
    """docstring for test_parse_all_variants"""
    parsed_variant = parse_variant(one_variant, parsed_case,
                                  rank_results_header=rank_results_header)

    assert parsed_variant['chromosome'] == '1'
    assert parsed_variant['rank_result']['Consequence'] == 1

def test_parse_small_sv(one_sv_variant, parsed_case):
    parsed_variant = parse_variant(one_sv_variant, parsed_case)

    assert parsed_variant['category'] == 'sv'
    assert parsed_variant['sub_category'] == one_sv_variant['info_dict']['SVTYPE'][0].lower()
    assert parsed_variant['position'] == int(one_sv_variant['POS'])

def test_parse_many_snvs(variants, parsed_case):
    """docstring for test_parse_all_variants"""

    for variant in variants:
        parsed_variant = parse_variant(variant, parsed_case)
        assert parsed_variant['chromosome'] == variant['CHROM']

def test_parse_many_svs(sv_variants, parsed_case):
    """docstring for test_parse_all_variants"""

    for variant in sv_variants:
        try:
            parsed_variant = parse_variant(variant, parsed_case)
        except VcfError:
            for info in variant['info_dict']:
                print(info, variant_dict['info'])
            assert False
        assert parsed_variant['chromosome'] == variant['CHROM']

