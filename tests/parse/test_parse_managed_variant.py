from scout.parse.variant.managed_variant import parse_managed_variant_lines


def test_parse_managed_variant_lines():
    """Test parsing managed variant csv"""

    ## GIVEN an iterable with managed variant lines
    mv_lines = [
        "##my_csv_file",
        "#chromosome;position;end;reference;alternative;category;sub_category;description\n",
        "14;76548781;76548781;CTGGACC;G;snv;indel;IFT43 indel test\n",
        "17;48696925;48696925;G;T;snv;snv;CACNA1G intronic test\n",
        "7;124491972;124491972;C;A;snv;snv;POT1 test snv\n",
    ]
    nr_mvs = len([line for line in mv_lines if not line.startswith("#")])

    ## WHEN parsing managed variant lines
    mvs = parse_managed_variant_lines(mv_lines)

    # one dict is returned for each line
    assert len(mvs) == nr_mvs
    # and some mv content is parsed to the given key
    assert mvs[0]["chromosome"] == "14"
    assert mvs[0]["position"] == "76548781"
    assert mvs[0]["description"] == "IFT43 indel test"
