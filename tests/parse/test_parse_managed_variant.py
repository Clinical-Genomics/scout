from scout.parse.variant.managed_variant import parse_managed_variant_lines


def test_parse_managed_variant_lines(managed_variants_lines):
    """Test parsing managed variant csv"""

    ## GIVEN an iterable with managed variant lines
    nr_mvs = len([line for line in managed_variants_lines if not line.startswith("#")])

    ## WHEN parsing managed variant lines
    mvs = parse_managed_variant_lines(managed_variants_lines)

    # one dict is returned for each line
    assert len(mvs) == nr_mvs
    # and some mv content is parsed to the given key
    assert mvs[0]["chromosome"] == "14"
    assert mvs[0]["position"] == "76548781"
    assert mvs[0]["description"] == "IFT43 indel test"
