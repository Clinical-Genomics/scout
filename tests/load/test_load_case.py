from scout.load.case import load_case

def test_load_case(case_obj, panel_database, gene_panels, default_panels, institute_obj, parsed_user):
    adapter = panel_database
    adapter.add_institute(institute_obj)
    adapter.getoradd_user(
        email=parsed_user['email'],
        name=parsed_user['name'],
        location=parsed_user['location'],
        institutes=parsed_user['institutes']
    )
    
    # GIVEN a database without cases
    assert adapter.cases().count() == 0
    # WHEN loading a case
    load_case(
        adapter=adapter,
        case_obj=case_obj,
        update=False,
        gene_panels=gene_panels,
        default_panels=default_panels
    )
    # THEN assert that the case have been loaded with correct info
    assert adapter.cases().count() == 1
    loaded_case = panel_database.case(institute_id=case_obj['owner'], case_id=case_obj['display_name'])
    
    assert loaded_case.case_id == case_obj['case_id']

    assert len(loaded_case.gene_panels) > 0
    
    for panel in loaded_case.gene_panels:
        assert panel.panel_name in gene_panels

    assert len(loaded_case.default_panels) > 0
    for panel in loaded_case.default_panels:
        assert panel.panel_name in gene_panels
