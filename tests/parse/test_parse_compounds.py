import logging
from scout.parse.compound import parse_compounds

def test_parse_compounds(parsed_case):
    variant = {
        'variant_id':'7_117175580_C_A',
        'compound_variants':{
            parsed_case['display_name']:[
                {
                    'variant_id':'7_117175579_AT_A',
                    'compound_score': 32
                }
            ]
        }
    }
    
    compounds = parse_compounds(
        variant=variant, 
        case=parsed_case, 
        variant_type='clinical'
    )
    compound = compounds[0]
    
    assert compound['display_name'] == '7_117175579_AT_A'
    assert compound['score'] == 32.0