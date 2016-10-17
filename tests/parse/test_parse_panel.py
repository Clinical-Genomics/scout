from scout.parse.panel import (parse_gene_panel, parse_genes)

def test_get_full_list_panel(panel_info):
    owner = 'cust000'
    panel = parse_gene_panel(panel_info, institute=owner)
    
    assert panel['institute'] == owner
    assert panel['id'] == panel_info['name']
    assert len(panel['genes']) == 3
    assert set(panel['genes']) == set(['POLD1', 'SRY', 'SLC19A2'])

def test_parse_genes(panel_info):
    genes = set(parse_genes(panel_info['file'], 'FullList'))
    
    assert genes == set(['POLD1', 'RBBP7', 'HNRNPU', 'SRY', 
                         'SLC19A2', 'CDK4'])