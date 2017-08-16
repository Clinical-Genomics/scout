from scout.load.case import load_case

def test_load_case(case_obj, panel_database):
    adapter = panel_database

    # GIVEN a database with institute, user, genes, panel but no cases
    assert adapter.gene_panels().count() > 0
    assert adapter.users().count() > 0
    assert adapter.institutes().count() > 0
    # WHEN loading a case
    adapter._add_case(case_obj)
    # THEN assert that the case have been loaded with correct info
    assert adapter.cases().count() == 1
    loaded_case = adapter.case(case_obj['_id'])
    
    assert loaded_case['case_id'] == case_obj['case_id']

    assert len(loaded_case['panels']) > 0
    
    for panel in loaded_case['panels']:
        assert panel['display_name']
