from scout.parse.hpo import (parse_hpo_phenotype, parse_hpo_phenotypes)

def test_parse_hpo_term(hpo_terms_handle):
    header = hpo_terms_handle.next()
    first_term = hpo_terms_handle.next()
    hpo_info = parse_hpo_phenotype(first_term)
    
    assert hpo_info['hpo_id'] == first_term.rstrip().split('\t')[0]
    assert hpo_info['description'] == first_term.rstrip().split('\t')[1]
    assert hpo_info['hgnc_symbol'] == first_term.rstrip().split('\t')[3]

def test_parse_hpo_terms(hpo_terms_handle):
    hpo_terms = parse_hpo_phenotypes(hpo_terms_handle)
    
    for hpo_id in hpo_terms:
        assert hpo_terms[hpo_id]['hpo_id'] == hpo_id
