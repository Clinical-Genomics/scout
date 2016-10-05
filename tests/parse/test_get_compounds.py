import logging
from scout.parse import parse_compounds

def test_get_genotype(compound_variant, vcf_case):
    compounds = parse_compounds(
        variant=compound_variant, 
        case=vcf_case, 
        variant_type='clinical'
    )
    compound = compounds[0]
    
    assert compound['display_name'] == '7_117175579_AT_A'
    assert compound['score'] == 32.0