from scout.parse.variant.conservation import (parse_conservation, parse_conservations)

def test_parse_conservation(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with some GERP information
    variant.INFO['dbNSFP_GERP___RS'] = 3.7
    ## WHEN parsing conservation
    ## THEN assert that the field is parsed correct
    assert parse_conservation(variant, 'dbNSFP_GERP___RS') == ['Conserved']

def test_parse_conservation_multiple_terms(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple GERP annotations
    variant.INFO['dbNSFP_GERP___RS'] = 3.7, -0.34

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned
    assert parse_conservation(variant, 'dbNSFP_GERP___RS') == ['Conserved', 'NotConserved']

def test_parse_conservations(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple conservation annotations
    variant.INFO['dbNSFP_GERP___RS'] = 4.6,0
    variant.INFO['dbNSFP_phastCons100way_vertebrate'] = 0.8
    variant.INFO['dbNSFP_phyloP100way_vertebrate'] = 2.4

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned

    conservations = parse_conservations(variant)

    assert conservations['gerp'] == ['Conserved', 'NotConserved']
    assert conservations['phast'] == ['Conserved']
    assert conservations['phylop'] == ['NotConserved']
