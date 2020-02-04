from scout.load.setup import setup_scout


def test_setup_scout(real_adapter):
    """Test to populate a demo instance of scout"""
    adapter = real_adapter
    ## GIVEN an empty adapter
    assert adapter.hgnc_collection.find_one() is None

    ## WHEN setting up a demo instance of scout
    setup_scout(adapter=adapter, demo=True)

    ## THEN make sure that stuff has been added
    assert adapter.hgnc_collection.find_one()
