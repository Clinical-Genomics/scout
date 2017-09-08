
def test_load_panel(gene_database, panel_info):
    # GIVEN an database with genes but no panels
    adapter = gene_database
    assert adapter.gene_panels().count() == 0
    
    # WHEN loading a gene panel
    adapter.load_panel(
        panel_info=panel_info
    )
    
    # THEN make sure that the panel is loaded
    
    assert adapter.gene_panel(panel_id=panel_info['panel_name'])