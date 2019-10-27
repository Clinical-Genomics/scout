from scout.server.links import get_variant_links

def test_get_variant_links(variant_obj):
    ## GIVEN a variant object without links
    assert 'thousandg_link' not in variant_obj
    ## WHEN fetching the variant links
    links = get_variant_links(variant_obj)
    ## THEN check that links are returned
    assert 'thousandg_link' in links