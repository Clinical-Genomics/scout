from scout.build.disease import build_disease_term
from scout.models.phenotype_term import DiseaseTerm

def test_build_disease_term(adapter):
    ## GIVEN some disease info and a adapter with a gene
    disease_info = {
        'mim_number': 615349,
        'description': "EHLERS-DANLOS SYNDROME, PROGEROID TYPE, 2",
        'hgnc_symbols': set(['B3GALT6']),
        'inheritance': set(['AR']),
    }
    alias_genes = {}
    alias_genes['B3GALT6'] = {
            'true': 17978,
            'ids': [17978],
        }
    
    ## WHEN building the disease term
    disease_obj = build_disease_term(disease_info, alias_genes)
    
    ## THEN assert the term is on the correct format
    
    assert disease_obj['_id'] == disease_obj['disease_id'] == "OMIM:615349"
    assert disease_obj['inheritance'] == ['AR']
    assert disease_obj['genes'] == [17978]
    assert disease_obj['source'] == 'OMIM'
    
    assert isinstance(disease_obj, DiseaseTerm)