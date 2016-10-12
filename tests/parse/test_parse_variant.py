from codecs import open
from scout.parse import parse_variant, parse_case
from vcf_parser import VCFParser

def test_parse_minimal(minimal_snv, minimal_case):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(minimal_snv, minimal_case, variant_type='clinical')
    
    assert parsed_variant['position'] == int(minimal_snv['POS'])
    assert parsed_variant['category'] == 'snv'

# def test_parse_all_variants(variant_file, ped_file):
#     """docstring for test_parse_all_variants"""
#     print(ped_file)
#     case = parse_case(
#         case_lines=open(ped_file, 'r'),
#         owner='cust000'
#     )
#     variants = VCFParser(infile=variant_file)
#     for variant in variants:
#         print(variant)

def test_parse_small_sv(minimal_sv, minimal_case):
    parsed_variant = parse_variant(minimal_sv, minimal_case)
    
    assert parsed_variant['category'] == 'sv'
    assert parsed_variant['sub_category'] == 'BND'
    assert parsed_variant['position'] == int(minimal_sv['POS'])
    assert parsed_variant['hgnc_symbols'] == ['NUDC']
    
# def test_parse_all_svs(sv_file, ped_file):
#     """docstring for test_parse_all_variants"""
#     print(ped_file)
#     case = parse_case(
#         case_lines=open(ped_file, 'r'),
#         owner='cust000'
#     )
#     variants = VCFParser(infile=sv_file)
#     from pprint import pprint as pp
#     for variant in variants:
#         pp(variant)

# def test_parse_variant(setup_database, vcf_case, get_institute):
#     variant_parser = VCFParser(infile=one_variant)
#     variants = []
#     individuals = variant_parser.individuals
#     scout_individuals = {ind_id:ind_id for ind_id in individuals}
#
#     for variant in variant_parser:
#         variants.append(variant)
#     variant = variants[0]
#     variant = parse_variant(
#                         variant_dict=variant,
#                         case=vcf_case,
#                         variant_type='clinical',
#                     )
#
#     assert variant['chromosome'] == '14'
#     assert variant['reference'] == 'C'
#     assert variant['alternative'] == 'A'
#
#
#     assert len(variant['genes']) == 2
#     assert len(variant['compounds']) == 3
