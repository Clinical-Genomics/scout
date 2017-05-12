from scout.parse.variant.conservation import (parse_conservation, parse_conservations)

def test_parse_conservation(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with some GERP information
    variant.INFO['GERP++_RS_prediction_term'] = 'Conserved'
    ## WHEN parsing conservation
    ## THEN assert that the field is parsed correct
    assert parse_conservation(variant, 'GERP++_RS_prediction_term') == ['Conserved']

def test_parse_conservation_wrong_term(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with wrong GERP information
    variant.INFO['GERP++_RS_prediction_term'] = 'Conservation'
    ## WHEN parsing conservation
    ## THEN assert that nothing is returned
    assert parse_conservation(variant, 'GERP++_RS_prediction_term') == []

def test_parse_conservation_multiple_terms(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple GERP annotations
    variant.INFO['GERP++_RS_prediction_term'] = 'Conserved, NotConserved'

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned
    assert parse_conservation(variant, 'GERP++_RS_prediction_term') == ['Conserved', 'NotConserved']

def test_parse_conservations(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple conservation annotations
    variant.INFO['GERP++_RS_prediction_term'] = 'Conserved,NotConserved'
    variant.INFO['phastCons100way_vertebrate_prediction_term'] = 'Conserved'
    variant.INFO['phyloP100way_vertebrate_prediction_term'] = 'NotConserved'

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned

    conservations = parse_conservations(variant)
    
    assert conservations['gerp'] == ['Conserved', 'NotConserved']
    assert conservations['phast'] == ['Conserved']
    assert conservations['phylop'] == ['NotConserved']