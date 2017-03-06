from scout.build.hpo import build_hpo_term

def test_build_hpo_term_non_existing_genes(adapter):
    ## GIVEN a hpo term
    hpo_info = {
        'hpo_id':"HP:0000878",
        'description': "11 pairs of ribs",
        'hgnc_symbols': ['B3GALT6', 'RBBP8']
    }
    ## WHEN building the hpo term
    hpo_obj = build_hpo_term(hpo_info, {})
    ## THEN assert that the term has the correct information
    assert hpo_obj['_id'] == hpo_obj['hpo_id'] == hpo_info['hpo_id']    
    assert hpo_obj['description'] == hpo_info['description']
    ## The adapter has no genes loaded so we expect this to be 0
    assert len(hpo_obj['genes']) == 0

def test_build_hpo_term_with_genes(adapter):
    ## GIVEN a hpo term and a adapter with genes
    hpo_info = {
        'hpo_id':"HP:0000878",
        'description': "11 pairs of ribs",
        'hgnc_symbols': ['B3GALT6', 'RBBP8']
    }
    genes = {}
    genes['B3GALT6'] = {
            'hgnc_id': 17978,
            'hgnc_symbol': 'B3GALT6',
            'build': '37'
        }
    
    genes['RBBP8'] = {
            'hgnc_id': 9891,
            'hgnc_symbol': 'RBBP8',
            'build': '37'
        }
    
    ## WHEN building the hpo term
    hpo_obj = build_hpo_term(hpo_info, genes)
    ## THEN assert that the term has the correct information
    assert hpo_obj['_id'] == hpo_obj['hpo_id'] == hpo_info['hpo_id']    
    ## The adapter has no genes loaded so we expect this to be 0
    assert len(hpo_obj['genes']) == 2
    assert set(hpo_obj['genes']) == set([17978, 9891])

def test_build_hpo_term_non_existing_gene(adapter):
    ## GIVEN a hpo term and a adapter with genes
    hpo_info = {
        'hpo_id':"HP:0000878",
        'description': "11 pairs of ribs",
        'hgnc_symbols': ['B3GALT6', 'RBBP8']
    }
    genes = {}
    genes['B3GALT6'] = {
            'hgnc_id': 17978,
            'hgnc_symbol': 'B3GALT6',
            'build': '37'
        }
    
    
    ## WHEN building the hpo term
    hpo_obj = build_hpo_term(hpo_info, genes)
    ## THEN assert that the term has the correct information
    assert hpo_obj['_id'] == hpo_obj['hpo_id'] == hpo_info['hpo_id']    
    ## The adapter has no genes loaded so we expect this to be 0
    assert len(hpo_obj['genes']) == 1
    assert hpo_obj['genes'] == [17978]
