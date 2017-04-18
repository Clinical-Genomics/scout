# -*- coding: utf-8 -*-
from scout.parse.variant.compound import parse_compounds


def test_parse_compounds(case_obj):
    variant = {
        'variant_id': '7_117175580_C_A',
        'compound_variants': {
            case_obj['display_name']: [{
                'variant_id': '7_117175579_AT_A',
                'compound_score': 32
            }]
        }
    }

    compounds = parse_compounds(variant=variant, case=case_obj, variant_type='clinical')
    compound = compounds[0]

    assert compound['display_name'] == '7_117175579_AT_A'
    assert compound['score'] == 32.0
