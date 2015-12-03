import logging
from scout.ext.backend.utils import get_compounds

def test_get_genotype(compound_variant, vcf_case):
    compounds = get_compounds(
        variant=compound_variant, 
        case=vcf_case, 
        variant_type='clinical'
    )
    compound = compounds[0]
    
    assert compound.display_name == '7_117175579_AT_A'
    assert compound.combined_score == 32.0