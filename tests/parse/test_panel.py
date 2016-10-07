from scout.parse.panel import (parse_gene_panel, parse_genes)

gene_list = "tests/fixtures/gene_lists/gene_list_test.txt"

def test_get_full_list_panel():
    
    panel_info = {
        'file': gene_list,
        'type': 'clinical',
        'name': 'FullList', 
        'version': 0.1, 
        'full_name': 'FullList', 
        'date': 'Today',
        
    }
    panel = parse_gene_panel(panel_info)
    
    assert len(panel['genes']) == 6
    assert set(panel['genes']) == set(['POLD1', 'RBBP7', 'HNRNPU', 'SRY', 
                                        'SLC19A2', 'CDK4'])

def test_parse_genes():
    genes = set(parse_genes(gene_list, 'FullList'))
    
    assert genes == set(['POLD1', 'RBBP7', 'HNRNPU', 'SRY', 
                         'SLC19A2', 'CDK4'])