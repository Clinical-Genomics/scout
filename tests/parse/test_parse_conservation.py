from scout.parse.variant.conservation import (parse_conservation, parse_conservations)

def test_parse_conservation():
    variant = {
        'info_dict':{
            'GERP++_RS_prediction_term': ['Conserved']
        }
    }
    assert parse_conservation(variant, 'GERP++_RS_prediction_term') == ['Conserved']

def test_parse_conservation_wrong_term():
    variant = {
        'info_dict':{
            'GERP++_RS_prediction_term': ['Conservation']
        }
    }
    assert parse_conservation(variant, 'GERP++_RS_prediction_term') == []

def test_parse_conservation_multiple_terms():
    variant = {
        'info_dict':{
            'GERP++_RS_prediction_term': ['Conserved', 'NotConserved']
        }
    }
    assert parse_conservation(variant, 'GERP++_RS_prediction_term') == ['Conserved', 'NotConserved']

def test_parse_conservations():
    variant = {
        'info_dict':{
            'GERP++_RS_prediction_term': ['Conserved', 'NotConserved'],
            'phastCons100way_vertebrate_prediction_term': ['Conserved'],
            'phyloP100way_vertebrate_prediction_term': ['NotConserved'],
        }
    }
    conservations = parse_conservations(variant)
    
    assert conservations['gerp'] == ['Conserved', 'NotConserved']
    assert conservations['phast'] == ['Conserved']
    assert conservations['phylop'] == ['NotConserved']