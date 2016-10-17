from scout.parse import parse_variant, parse_case
from scout.exceptions import VcfError

def test_parse_minimal(minimal_snv, minimal_case):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(minimal_snv, minimal_case, variant_type='clinical')
    
    assert parsed_variant['position'] == int(minimal_snv['POS'])
    assert parsed_variant['category'] == 'snv'

def test_parse_one_snv_from_file(one_file_variant, parsed_case):
    """docstring for test_parse_all_variants"""

    for variant in one_file_variant:
        parsed_variant = parse_variant(variant, parsed_case)
        assert parsed_variant['chromosome'] == '1'

def test_parse_small_sv(minimal_sv, minimal_case):
    parsed_variant = parse_variant(minimal_sv, minimal_case)
    
    assert parsed_variant['category'] == 'sv'
    assert parsed_variant['sub_category'] == 'bnd'
    assert parsed_variant['position'] == int(minimal_sv['POS'])
    assert parsed_variant['hgnc_symbols'] == ['NUDC']
    assert parsed_variant['mate_id'] == 'MantaBND:454:0:1:0:0:0:1'

def test_parse_one_sv_from_file(one_file_sv_variant, parsed_case):
    """docstring for test_parse_all_variants"""
    
    for variant in one_file_sv_variant:
        parsed_variant = parse_variant(variant, parsed_case)
        assert parsed_variant['chromosome'] == '1'

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

