from codecs import open
from scout.parse import parse_variant, parse_case
from vcf_parser import VCFParser
from scout.exceptions import VcfError

def test_parse_minimal(minimal_snv, minimal_case):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(minimal_snv, minimal_case, variant_type='clinical')
    
    assert parsed_variant['position'] == int(minimal_snv['POS'])
    assert parsed_variant['category'] == 'snv'

def test_parse_one_snv_from_file(one_file_variant, ped_file):
    """docstring for test_parse_all_variants"""
    print(ped_file)
    case = parse_case(
        case_lines=open(ped_file, 'r'),
        owner='cust000'
    )
    for variant in one_file_variant:
        parsed_variant = parse_variant(variant, case)
        assert parsed_variant['chromosome'] == '1'

def test_parse_small_sv(minimal_sv, minimal_case):
    parsed_variant = parse_variant(minimal_sv, minimal_case)
    
    assert parsed_variant['category'] == 'sv'
    assert parsed_variant['sub_category'] == 'bnd'
    assert parsed_variant['position'] == int(minimal_sv['POS'])
    assert parsed_variant['hgnc_symbols'] == ['NUDC']
    assert parsed_variant['mate_id'] == 'MantaBND:454:0:1:0:0:0:1'

def test_parse_one_sv_from_file(one_file_sv_variant, ped_file):
    """docstring for test_parse_all_variants"""
    print(ped_file)
    case = parse_case(
        case_lines=open(ped_file, 'r'),
        owner='cust000'
    )
    for variant in one_file_sv_variant:
        parsed_variant = parse_variant(variant, case)
        assert parsed_variant['chromosome'] == '1'
    
def test_parse_many_svs(sv_file, ped_file):
    """docstring for test_parse_all_variants"""
    case = parse_case(
        case_lines=open(ped_file, 'r'),
        owner='cust000'
    )
    variants = VCFParser(infile=sv_file)
    for variant in variants:
        try:
            parsed_variant = parse_variant(variant, case)
        except VcfError:
            for info in variant['info_dict']:
                print(info, variant_dict['info'])
            assert False
        assert parsed_variant['chromosome'] == variant['CHROM']

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
