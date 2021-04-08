from scout.parse.variant.deleteriousness import parse_cadd


def test_parse_cadd_info(cyvcf2_variant, case_obj):
    """Test parsing a variant that has CADD score in the info field"""

    variant = cyvcf2_variant

    # GIVEN a variant with CADD INFO field
    variant.INFO["CADD"] = 23
    cadd_score = parse_cadd(variant, [])

    # THEN the parse cadd function should return the expected value
    assert cadd_score == float(variant.INFO["CADD"])


def test_parse_cadd_transcripts(cyvcf2_variant, transcript_info):
    """Test parsing a variant that has CADD score in the transcript dictionary"""

    # GIVEN a variant with CADD score in transcript info
    transcript_info["cadd"] = 23.0

    cadd_score = parse_cadd(cyvcf2_variant, [transcript_info])

    # THEN the parse cadd function should return the expected value
    assert cadd_score == transcript_info["cadd"]
