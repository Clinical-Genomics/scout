from scout.parse.variant.ids import (
    parse_display_name,
    parse_document_id,
    parse_ids,
    parse_simple_id,
    parse_variant_id,
)
from scout.utils.md5 import generate_md5_key


def test_parse_simple_id():
    # GIVEN some coordinates
    chrom = "1"
    pos = "10"
    ref = "A"
    alt = "G"

    # WHEN parsing the simple id
    simple_id = parse_simple_id(chrom, pos, ref, alt)
    # THEN we should get a correct simple id
    assert simple_id == "_".join([chrom, pos, ref, alt])


def test_parse_variant_id():
    # GIVEN some coordinates
    chrom = "1"
    pos = "10"
    ref = "A"
    alt = "G"
    variant_type = "clinical"

    # WHEN parsing the variant id
    variant_id = parse_variant_id(chrom, pos, ref, alt, variant_type)
    # THEN we should get a correct variant id
    assert variant_id == generate_md5_key([chrom, pos, ref, alt, variant_type])


def test_parse_display_name():
    # GIVEN some coordinates
    chrom = "1"
    pos = "10"
    ref = "A"
    alt = "G"
    variant_type = "clinical"

    # WHEN parsing the display name
    variant_id = parse_display_name(chrom, pos, ref, alt, variant_type)
    # THEN we should get a correct display name
    assert variant_id == "_".join([chrom, pos, ref, alt, variant_type])


def test_parse_document_id():
    # GIVEN some variant information
    chrom = "1"
    pos = "10"
    ref = "A"
    alt = "G"
    case_id = "cust000_1"
    variant_type = "clinical"

    # WHEN parsing the document id
    variant_id = parse_document_id(chrom, pos, ref, alt, variant_type, case_id)
    # THEN we should get a correct md5 string back
    assert variant_id == generate_md5_key([chrom, pos, ref, alt, variant_type, case_id])


def test_parse_ids():
    # GIVEN some variant and case information
    chrom = "1"
    pos = 10
    ref = "A"
    alt = "G"
    case_id = "cust000_1"
    variant_type = "clinical"

    # WHEN parsing the variant ids
    variant_ids = parse_ids(chrom, pos, ref, alt, case_id, variant_type)

    # THEN we should get a dictionary with all ids back
    assert isinstance(variant_ids, dict)
    assert variant_ids["simple_id"] == "_".join([chrom, str(pos), ref, alt])
