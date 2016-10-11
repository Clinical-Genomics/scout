from scout.parse import parse_variant

def test_parse_minimal(minimal_snv, minimal_case):
    """Test to parse a minimal variant"""
    parsed_variant = parse_variant(minimal_snv, minimal_case, variant_type='clinical')
    
    assert parsed_variant['position'] == 10
    assert parsed_variant['end'] == 10
    assert parsed_variant['category'] == 'snv'

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
