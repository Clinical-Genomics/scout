def build_genotype(gt_call):
    """Build a genotype call

    Args:
        gt_call(dict)

    Returns:
        gt_obj(dict)

    gt_call = dict(
        sample_id = str,
        display_name = str,
        genotype_call = str,
        allele_depths = list, # int
        read_depth = int,
        genotype_quality = int,
        so = str, # STR type of reads that support allele: "a/a" where a in [SPANNING, FLANKING, INREPEAT]
    )

    """
    gt_obj = dict(
        sample_id=gt_call["individual_id"],
        display_name=gt_call["display_name"],
        genotype_call=gt_call.get("genotype_call"),
        allele_depths=[gt_call["ref_depth"], gt_call["alt_depth"]],
        read_depth=gt_call["read_depth"],
        alt_frequency=gt_call["alt_frequency"] or -1,
        genotype_quality=gt_call["genotype_quality"],
        so=gt_call["so"],
        ffpm=gt_call["ffpm"],
        split_read=gt_call["split_read"],
    )

    return gt_obj
