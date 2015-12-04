from scout.ext.backend.utils import get_gene_panel

gene_list = "tests/fixtures/gene_lists/gene_list_test.txt"

def test_get_full_list_panel():
    
    panel = get_gene_panel(
                list_file_name=gene_list, 
                institute_id='cust000', 
                panel_id='FullList', 
                panel_version=0.1, 
                display_name='FullList', 
                panel_date='Today'
    )
    assert len(panel.genes) == 6
    assert set(panel.genes) == set(['POLD1', 'RBBP7', 'HNRNPU', 'SRY', 
                                        'SLC19A2', 'CDK4'])

