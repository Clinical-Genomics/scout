from scout.load.panel import load_panel

def test_load_panel(gene_database, panel_info):
    # GIVEN an database with genes but no panels
    
    assert gene_database.gene_panels().count() == 0
    
    # WHEN loading a gene panel
    load_panel(
        adapter=gene_database, 
        panel_info=panel_info
    )
    
    # THEN make sure that the panel is loaded
    
    assert gene_database.gene_panel(panel_id=panel_info['panel_name'])