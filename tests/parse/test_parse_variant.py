from scout.parse import parse_variant

from vcf_parser import VCFParser

one_variant = "tests/fixtures/337334.one_variant.clinical.vcf"

def test_parse_variant(setup_database, vcf_case, get_institute):
    variant_parser = VCFParser(infile=one_variant)
    variants = []
    individuals = variant_parser.individuals
    scout_individuals = {ind_id:ind_id for ind_id in individuals}
    
    for variant in variant_parser:
        variants.append(variant)
    variant = variants[0]
    variant = parse_variant(
                        variant_dict=variant,
                        case=vcf_case,
                        variant_type='clinical',
                    )
    
    assert variant['chromosome'] == '14'
    assert variant['reference'] == 'C'
    assert variant['alternative'] == 'A'


    assert len(variant['genes']) == 2
    assert len(variant['compounds']) == 3
