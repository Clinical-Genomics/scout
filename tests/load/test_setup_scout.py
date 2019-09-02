from scout.load.setup import setup_scout

def test_setup_scout(real_adapter):
    """Test to populate a demo instance of scout"""
    adapter = real_adapter
    ## GIVEN an empty adapter
    assert sum(1 for i in adapter.all_genes()) == 0
    
    ## WHEN setting up a demo instance of scout
    setup_scout(adapter=adapter, demo=True)
    
    ## THEN make sure that stuff has been added
    assert sum(1 for i in adapter.all_genes()) > 0
    