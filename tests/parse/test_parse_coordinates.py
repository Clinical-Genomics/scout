"""Tests to parse coordinates"""

from scout.parse.variant.coordinates import (
    get_cytoband_coordinates,
    parse_coordinates,
    sv_end,
    sv_length,
)


def test_parse_coordinates_snv(mock_variant):
    """Test to parse the coordinates for a simple snv"""
    # GIVEN a cyvcf2 variant
    variant = mock_variant

    # WHEN parsing the coordinate info
    coordinates = parse_coordinates(variant, "snv")

    # THEN assert that they are correctly parsed
    assert coordinates["position"] == variant.POS
    assert coordinates["end"] == variant.end
    assert coordinates["length"] == len(variant.ALT)
    assert coordinates["sub_category"] == "snv"
    assert coordinates["mate_id"] is None
    assert (
        coordinates["cytoband_start"]
        == coordinates["cytoband_end"]
        == get_cytoband_coordinates(variant.CHROM, variant.POS, "37")
    )
    assert coordinates["end_chrom"] == variant.CHROM


def test_parse_coordinate_snv_build_38(mock_variant):
    """Test to parse the coordinates for a simple snv, genome assembly 38"""

    # GIVEN a cyvcf2 variant
    variant = mock_variant

    # WHEN parsing the coordinate info
    coordinates = parse_coordinates(variant, "snv", "38")

    # THEN assert that they are correctly parsed
    assert coordinates["position"] == variant.POS
    assert coordinates["end"] == variant.end
    assert coordinates["length"] == len(variant.ALT)
    assert coordinates["sub_category"] == "snv"
    assert coordinates["mate_id"] is None
    assert (
        coordinates["cytoband_start"]
        == coordinates["cytoband_end"]
        == get_cytoband_coordinates(variant.CHROM, variant.POS, "38")
    )
    assert coordinates["end_chrom"] == variant.CHROM


def test_parse_coordinates_indel(mock_variant):
    """Test to parse the coordinates for an indel"""
    mock_variant.ALT = "ACCC"
    mock_variant.end = 80000
    variant = mock_variant

    coordinates = parse_coordinates(variant, "snv")
    assert coordinates["position"] == variant.POS
    assert coordinates["end"] == variant.end
    assert coordinates["sub_category"] == "indel"
    assert coordinates["length"] == abs(len(variant.ALT[0]) - len(variant.REF))


def test_parse_coordinates_translocation(mock_variant):
    """Test to parse the coordinates for a translocation"""
    mock_variant.INFO = {"SVTYPE": "BND"}
    mock_variant.REF = "N"
    mock_variant.ALT = "N[hs37d5:12060532["
    mock_variant.POS = 724779
    mock_variant.end = 724779
    mock_variant.var_type = "sv"
    variant = mock_variant

    coordinates = parse_coordinates(variant, "sv")

    assert coordinates["position"] == variant.POS
    assert coordinates["end"] == 12060532
    assert coordinates["end_chrom"] == "hs37d5"
    assert coordinates["length"] == 10e10
    assert coordinates["sub_category"] == "bnd"


def test_parse_coordinates_translocation_same_chrom(mock_variant):
    """Test to parse the coordinates for a translocation on the same chromosome"""
    mock_variant.INFO = {"SVTYPE": "BND"}
    mock_variant.REF = "N"
    mock_variant.ALT = "N[1:12060532["
    mock_variant.POS = 724779
    mock_variant.end = 724779
    mock_variant.var_type = "sv"
    variant = mock_variant

    coordinates = parse_coordinates(variant, "sv")

    assert coordinates["position"] == variant.POS
    assert coordinates["end"] == 12060532
    assert coordinates["end_chrom"] == "1"
    assert coordinates["length"] == coordinates["end"] - coordinates["position"]
    assert coordinates["sub_category"] == "bnd"


def test_parse_coordinates_translocation_2(mock_variant):
    """Test to parse the coordinates for a translocation"""
    mock_variant.INFO = {"SVTYPE": "BND"}
    mock_variant.REF = "N"
    mock_variant.ALT = "N[GL000232.1:25141["
    mock_variant.POS = 724779
    mock_variant.end = 724779
    mock_variant.var_type = "sv"
    variant = mock_variant

    coordinates = parse_coordinates(variant, "sv")

    assert coordinates["position"] == variant.POS
    assert coordinates["end"] == 25141
    assert coordinates["end_chrom"] == "GL000232.1"
    assert coordinates["length"] == 10e10
    assert coordinates["sub_category"] == "bnd"


# parse length #


def test_get_sv_length_small_ins():
    """Test to get the length for a small insertion"""
    # GIVEN an insertion with whole sequence in alt field
    # Pos and end is same for insertions
    pos = end = 144343218
    svlen = 296
    chrom = end_chrom = "1"

    # WHEN parsing the length
    length = sv_length(pos, end, chrom, end_chrom, svlen)

    # THEN assert that the length is correct
    assert length == 296


def test_get_sv_length_large_ins_no_length():
    """Test to get the length for a small insertion wihtout length"""
    # GIVEN an imprecise insertion
    # Pos and end is same for insertions
    pos = end = 133920667
    svlen = None
    chrom = end_chrom = "1"

    # WHEN parsing the length
    length = sv_length(pos, end, chrom, end_chrom, svlen)

    # THEN assert that the length is correct
    assert length == -1


def test_get_sv_length_translocation():
    """Test to get the length for a translocation on different chromosomes"""
    # GIVEN an translocation with different start and end chromosomes
    pos = 726044
    end = None
    svlen = None
    chrom = "1"
    end_chrom = "10"

    # WHEN parsing the length
    length = sv_length(pos, end, chrom, end_chrom, svlen)

    # THEN assert that the length is "infinite"
    assert length == 10e10


def test_get_sv_length_translocation_same_chrom():
    """Test to get the length for a translocation on different chromosomes"""
    # GIVEN an translocation with different start and end chromosomes
    pos = 726044
    end = 16457990
    svlen = None
    chrom = end_chrom = "1"

    # WHEN parsing the length
    length = sv_length(pos, end, chrom, end_chrom, svlen)

    # THEN assert that the length is "infinite"
    assert length == end - pos


def test_get_sv_length_cnvnator_del():
    """Test to get the length cnvnator formated deletion"""
    # GIVEN an cnvnator type deletion
    pos = 1
    end = 10000
    svlen = -10000
    chrom = end_chrom = "1"

    # WHEN parsing the length
    length = sv_length(pos, end, chrom, end_chrom, svlen)

    # THEN assert that the length is correct
    assert length == 10000


def test_get_sv_length_del_no_length():
    """Test to get the length for a deletion without length"""
    # GIVEN an deletion without len
    pos = 869314
    end = 870246
    svlen = None
    chrom = end_chrom = "1"

    # WHEN parsing the length
    length = sv_length(pos, end, chrom, end_chrom, svlen)

    # THEN assert that the length is correct
    assert length == end - pos


# SVs are much harder since there are a lot of corner cases
# Most SVs (except translocations) have END annotated in INFO field
# The problem is that many times END==POS and then we have to do some magic on our own


def test_get_end_tiddit_translocation():
    """Test to get the end position for a translocation in tiddit format"""
    # GIVEN a translocation
    _end = 12060532
    alt = f"N[hs37d5:{_end}["
    pos = 724779

    # WHEN parsing the end coordinate
    end = sv_end(pos, alt, svend=None, svlen=None)

    # THEN assert that the end is the same as en coordinate described in alt field
    assert end == _end


def test_get_end_deletion():
    """Test to get the end position for a SV deletion"""
    # GIVEN a translocation
    alt = "<DEL>"
    pos = 869314
    svend = 870246
    svlen = None

    # WHEN parsing the end coordinate
    end = sv_end(pos, alt, svend, svlen)

    # THEN assert that the end is the same as en coordinate described in alt field
    assert end == svend
