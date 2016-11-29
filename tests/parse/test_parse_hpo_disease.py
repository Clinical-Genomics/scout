from scout.parse.hpo import (parse_hpo_disease, parse_hpo_diseases)

def test_parse_disease(hpo_disease_handle):
    header = hpo_disease_handle.next()
    first_disease = hpo_disease_handle.next()
    disease_info = parse_hpo_disease(first_disease)
    
    assert disease_info['disease_nr'] == int(first_disease.rstrip().split('\t')[0].split(':')[1])
    assert disease_info['hgnc_symbol'] == first_disease.rstrip().split('\t')[1]
    assert disease_info['hpo_id'] == first_disease.rstrip().split('\t')[3]

def test_parse_diseases(hpo_disease_handle):
    diseases = parse_hpo_diseases(hpo_disease_handle)
    
    for disease_nr in diseases:
        assert diseases[disease_nr]['disease_nr'] == disease_nr