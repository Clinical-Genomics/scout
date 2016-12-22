from scout.load.case import load_case

def test_load_case(case_obj, panel_database, gene_panels, default_panels):
    # GIVEN a database without cases
    assert panel_database.cases().count() == 0
    # WHEN loading a case
    load_case(
        adapter=panel_database, 
        case_obj=case_obj, 
        update=False, 
        gene_panels=gene_panels,
        default_panels=default_panels
    )
    # THEN assert that the case have been loaded with correct info
    assert panel_database.cases().count() == 1
    loaded_case = panel_database.case(institute_id=case_obj['owner'], case_id=case_obj['display_name'])
    assert loaded_case.case_id == case_obj['case_id']
    
    assert len(loaded_case.gene_panels) > 0
    for panel in loaded_case.gene_panels:
        assert panel.panel_name in gene_panels

    assert len(loaded_case.default_panels) > 0
    for panel in loaded_case.default_panels:
        assert panel.panel_name in gene_panels
    