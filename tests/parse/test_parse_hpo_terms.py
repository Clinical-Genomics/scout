from scout.parse.hpo import (parse_hpo_phenotype, parse_hpo_phenotypes)

def test_parse_hpo_line():
    ## GIVEN a line that describes a hpo term
    hpo_line = "HP:0000878\t11 pairs of ribs\t126792\tB3GALT6"
    ## WHEN parsing the line
    hpo_info = parse_hpo_phenotype(hpo_line)
    ## THEN assert that the correct information was parsed
    assert hpo_info['hpo_id'] == "HP:0000878"
    assert hpo_info['description'] == "11 pairs of ribs"
    assert hpo_info['hgnc_symbol'] == "B3GALT6"

def test_parse_hpo_lines():
    ## GIVEN some lines that correspends to a hpo file
    hpo_lines = [
        "#Format: HPO-ID<tab>HPO-Name<tab>Gene-ID<tab>Gene-Name",
        "HP:0000878\t11 pairs of ribs\t126792\tB3GALT6",
        "HP:0000878\t11 pairs of ribs\t5932\tRBBP8"
    ]
    ## WHEN parsing the lines
    hpo_dict = parse_hpo_phenotypes(hpo_lines)
    ## THEN assert that the correct information was parsed
    assert len(hpo_dict) == 1
    assert "HP:0000878" in hpo_dict
    assert set(hpo_dict['HP:0000878']['hgnc_symbols']) == set(['B3GALT6', 'RBBP8'])

def test_parse_hpo_term(hpo_terms_handle):
    header = next(hpo_terms_handle)
    first_term = next(hpo_terms_handle)
    hpo_info = parse_hpo_phenotype(first_term)
    
    assert hpo_info['hpo_id'] == first_term.rstrip().split('\t')[0]
    assert hpo_info['description'] == first_term.rstrip().split('\t')[1]
    assert hpo_info['hgnc_symbol'] == first_term.rstrip().split('\t')[3]

def test_parse_hpo_terms(hpo_terms_handle):
    hpo_terms = parse_hpo_phenotypes(hpo_terms_handle)
    
    for hpo_id in hpo_terms:
        assert hpo_terms[hpo_id]['hpo_id'] == hpo_id
