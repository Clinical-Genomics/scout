def build_genotype(gt_call: dict) -> dict:
    """Build a genotype call

    Format tags only expected on some variant types are set if present.
    """
    gt_obj = dict(
        sample_id=gt_call["individual_id"],
        display_name=gt_call["display_name"],
        genotype_call=gt_call.get("genotype_call"),
        allele_depths=[gt_call["ref_depth"], gt_call["alt_depth"]],
        read_depth=gt_call["read_depth"],
        alt_frequency=gt_call["alt_frequency"] or -1,
        genotype_quality=gt_call["genotype_quality"],
    )

    for format_tag in ["alt_mc", "copy_number", "ffpm", "sdp", "sdr", "so", "split_read"]:
        if format_tag in gt_call:
            gt_obj[format_tag] = gt_call[format_tag]

    return gt_obj
