from scout.server.links import get_variant_links
from scout server.utils import find_index

def test_get_variant_links(variant_obj):
    ## GIVEN a variant object without links
    assert 'thousandg_link' not in variant_obj
    ## WHEN fetching the variant links
    links = get_variant_links(variant_obj)
    ## THEN check that links are returned
    assert 'thousandg_link' in links

def test_find_index():

    # Test get index for a bam file:
    alignment = "test.bam"
    index = find_index(alignment)
    assert index == "test.bam.bai"

    # assert get index for a cram file
    alignment = "test.cram"
    index = find_index(alignment)
    assert index == "test.cram.crai"
