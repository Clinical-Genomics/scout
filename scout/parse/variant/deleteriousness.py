def parse_cadd(variant, transcripts):
    """Check if the cadd phred score is annotated

    Args:
        variant(cyvcf2.Variant)
        transcripts(list(dict))

    Returns:
        cadd(int)
    """
    cadd = 0
    cadd_keys = ["CADD", "CADD_PHRED"]
    for key in cadd_keys:
        cadd = variant.INFO.get(key, 0)
        if cadd:
            return float(cadd)

    for transcript in transcripts:
        cadd_entry = transcript.get("cadd")
        if cadd_entry and cadd_entry > cadd:
            cadd = cadd_entry

    return cadd
