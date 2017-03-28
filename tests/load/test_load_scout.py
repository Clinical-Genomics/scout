from scout.load.all import load_scout

def test_load_scout(panel_database, scout_config):
    adapter = panel_database
    # GIVEN a database with genes
    assert panel_database.cases().count() == 0
    # WHEN loading a case with variants
    load_scout(
        adapter=panel_database, 
        config=scout_config
    )
    # THEN assert they are loded
    assert panel_database.cases().count() == 1