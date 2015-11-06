from scout.ext.backend.utils import get_gene_lists

LIST_LINES = [
    "##Database=<ID=test.txt,Version=0.1,Date=20151021,Acronym=TEST,"\
    "Complete_name=TESTING",
    "#Chromosome	Gene_start	Gene_stop	HGNC_symbol	Clinical_db_gene_annotation",
    "11	818902	825573	PNPLA2	TEST",
    "6	97337189	97345757	NDUFAF4	TEST"
]

def test_get_gene_list():
    """docstring for test_get_gene_list"""
    panels = get_gene_lists(LIST_LINES, 'TEST_INST')
    
    test_panel = panels[0]
    
    assert test_panel.institute == 'TEST_INST'
    assert test_panel.panel_name == 'TEST'
    assert test_panel.version == 0.1
    assert test_panel.date == '20151021'
    assert test_panel.display_name == 'TESTING'
    assert test_panel.genes == ['PNPLA2', 'NDUFAF4']