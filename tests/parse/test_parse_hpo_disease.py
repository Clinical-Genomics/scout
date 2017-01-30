from scout.parse.hpo import (parse_hpo_disease, parse_hpo_diseases)

def test_parse_disease_lines():
    """Test how the parser behaves"""
    disease_lines = [
        "#Format: diseaseId<tab>gene-id<tab>gene-symbol",
        "OMIM:139500",
        "ORPHANET:1228",
        "DECIPHER:74",
        "OMIM:214500\t1130\tLYST",
    ]
    ## GIVEN a disease term without gene symbol
    ## WHEN parsing the line
    disease = parse_hpo_disease(disease_lines[1])
    ## THEN assert the info is correct
    assert disease['source'] == "OMIM"
    assert disease['disease_nr'] == 139500
    assert disease['hgnc_symbol'] == None

    ## GIVEN a disease term without gene symbol
    ## WHEN parsing the line
    disease = parse_hpo_disease(disease_lines[2])
    ## THEN assert the info is correct
    assert disease['source'] == "ORPHANET"
    assert disease['disease_nr'] == 1228
    assert disease['hgnc_symbol'] == None

    ## GIVEN a disease term without gene symbol
    ## WHEN parsing the line
    disease = parse_hpo_disease(disease_lines[3])
    ## THEN assert the info is correct
    assert disease['source'] == "DECIPHER"
    assert disease['disease_nr'] == 74
    assert disease['hgnc_symbol'] == None

    ## GIVEN a disease term without gene symbol
    ## WHEN parsing the line
    disease = parse_hpo_disease(disease_lines[4])
    ## THEN assert the info is correct
    assert disease['source'] == "OMIM"
    assert disease['disease_nr'] == 214500
    assert disease['hgnc_symbol'] == "LYST"

def test_parse_diseases_lines():
    ## GIVEN a iterable of disease lines
    disease_lines = [
        "#Format: diseaseId<tab>gene-id<tab>gene-symbol",
        "OMIM:300818	5277	PIGA",
        "OMIM:300868	5277	PIGA",
        "ORPHANET:447	5277	PIGA",
        "OMIM:101400	2263	FGFR2",
        "OMIM:101400	7291	TWIST1",
        "OMIM:139500",
    ]
    ## WHEN parsing the diseases
    diseases = parse_hpo_diseases(disease_lines)
    ## THEN assert that the diseases are parsed correct
    assert diseases["OMIM:300818"]['source'] == 'OMIM'
    assert diseases["OMIM:300818"]['hgnc_symbols'] == set(['PIGA'])

    assert diseases["ORPHANET:447"]['source'] == "ORPHANET"
    assert diseases["ORPHANET:447"]['hgnc_symbols'] == set(['PIGA'])

    assert diseases["OMIM:101400"]['source'] == 'OMIM'
    assert diseases["OMIM:101400"]['hgnc_symbols'] == set(['FGFR2','TWIST1'])

    assert diseases["OMIM:139500"]['source'] == 'OMIM'
    assert diseases["OMIM:139500"]['hgnc_symbols'] == set([])

def test_parse_diseases(hpo_disease_handle):
    ## GIVEN a iterable of disease lines
    ## WHEN parsing the diseases
    diseases = parse_hpo_diseases(hpo_disease_handle)
    ## THEN assert that the diseases are parsed correct
    for disease_id in diseases:
        source = disease_id.split(':')[0]
        disease_nr = int(disease_id.split(':')[1])
        
        disease_term = diseases[disease_id]
        assert disease_term['source'] == source
        assert disease_term['disease_nr'] == disease_nr
