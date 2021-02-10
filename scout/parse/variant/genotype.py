# encoding: utf-8
"""
parse_genotypes will try to collect and merge information from vcf with
genotypes called by multiple variant callers. This is a complex problem,
especially for Structural Variants. I will try to explain some of the specific
problems here.

## cnvnator
Calls copy number events such as deletions and duplications. Genotype calls
are simple and not that informative. It includes 'GT' and 'CN' wich estimates
the number of copies of an event. We will not use 'CN' since it is a bit
unclear at the moment.

## tiddit
Calls most type of structural events, specialized on translocations.
Uses 'DV' to describe number of paired ends that supports the event and
'RV' that are number of split reads that supports the event.

"""

GENOTYPE_MAP = {0: "0", 1: "1", -1: "."}


def parse_genotypes(variant, individuals, individual_positions):
    """Parse the genotype calls for a variant

    Args:
        variant(cyvcf2.Variant)
        individuals: List[dict]
        individual_positions(dict)
    Returns:
        genotypes(list(dict)): A list of genotypes
    """
    genotypes = []
    for ind in individuals:
        pos = individual_positions[ind["individual_id"]]
        genotypes.append(parse_genotype(variant, ind, pos))
    return genotypes


def parse_genotype(variant, ind, pos):
    """Get the genotype information in the proper format

    SV specific format fields:
    ##FORMAT=<ID=DV,Number=1,Type=Integer,Description="Number of paired-ends that support the event">
    ##FORMAT=<ID=PE,Number=1,Type=Integer,Description="Number of paired-ends that support the event">
    ##FORMAT=<ID=PR,Number=.,Type=Integer,Description="Spanning paired-read support for the ref and alt alleles in the order listed">
    ##FORMAT=<ID=RC,Number=1,Type=Integer,Description="Raw high-quality read counts for the SV">
    ##FORMAT=<ID=RCL,Number=1,Type=Integer,Description="Raw high-quality read counts for the left control region">
    ##FORMAT=<ID=RCR,Number=1,Type=Integer,Description="Raw high-quality read counts for the right control region">
    ##FORMAT=<ID=RR,Number=1,Type=Integer,Description="# high-quality reference junction reads">
    ##FORMAT=<ID=RV,Number=1,Type=Integer,Description="# high-quality variant junction reads">
    ##FORMAT=<ID=SR,Number=1,Type=Integer,Description="Number of split reads that support the event">

    STR specific format fields:
    ##FORMAT=<ID=LC,Number=1,Type=Float,Description="Locus coverage">
    ##FORMAT=<ID=REPCI,Number=1,Type=String,Description="Confidence interval for REPCN">
    ##FORMAT=<ID=REPCN,Number=1,Type=String,Description="Number of repeat units spanned by the allele">
    ##FORMAT=<ID=SO,Number=1,Type=String,Description="Type of reads that support the allele; can be SPANNING, FLANKING, or INREPEAT meaning that the reads span, flank, or are fully contained in the repeat">
    ##FORMAT=<ID=ADFL,Number=1,Type=String,Description="Number of flanking reads consistent with the allele">
    ##FORMAT=<ID=ADIR,Number=1,Type=String,Description="Number of in-repeat reads consistent with the allele">
    ##FORMAT=<ID=ADSP,Number=1,Type=String,Description="Number of spanning reads consistent with the allele">

    Args:
        variant(cyvcf2.Variant)
        ind_id(dict): A dictionary with individual information
        pos(int): What position the ind has in vcf

    Returns:
        gt_call(dict)

    """
    gt_call = {}
    ind_id = ind["individual_id"]

    gt_call["individual_id"] = ind_id
    gt_call["display_name"] = ind["display_name"]

    # Fill the object with the relevant information:
    if "GT" in variant.FORMAT:
        genotype = variant.genotypes[pos]
        ref_call = genotype[0]
        alt_call = genotype[1]

        gt_call["genotype_call"] = "/".join([GENOTYPE_MAP[ref_call], GENOTYPE_MAP[alt_call]])

    # STR specific
    str_so = None
    if "SO" in variant.FORMAT:
        try:
            so = variant.format("SO")[pos]
            if so not in [None, -1]:
                str_so = str(so)
        except ValueError as e:
            pass

    gt_call["so"] = str_so

    (spanning_ref, spanning_alt) = _parse_format_entry(variant, pos, "ADSP")
    (flanking_ref, flanking_alt) = _parse_format_entry(variant, pos, "ADFL")
    (inrepeat_ref, inrepeat_alt) = _parse_format_entry(variant, pos, "ADIR")

    # SV specific
    paired_end_alt = None
    paired_end_ref = None
    split_read_alt = None
    split_read_ref = None

    # Check if PE is annotated
    # This is the number of paired end reads that supports the variant
    if "PE" in variant.FORMAT:
        try:
            value = int(variant.format("PE")[pos])
            if value >= 0:
                paired_end_alt = value
        except ValueError as e:
            pass

    # Check if PR is annotated
    # Number of paired end reads that supports ref and alt
    if "PR" in variant.FORMAT:
        values = variant.format("PR")[pos]
        try:
            alt_value = int(values[1])
            ref_value = int(values[0])
            if alt_value >= 0:
                paired_end_alt = alt_value
            if ref_value >= 0:
                paired_end_ref = ref_value
        except ValueError as r:
            pass

    # Check if 'SR' is annotated
    if "SR" in variant.FORMAT:
        values = variant.format("SR")[pos]
        alt_value = 0
        ref_value = 0
        if len(values) == 1:
            alt_value = int(values[0])
        if len(values) == 2:
            alt_value = int(values[1])
            ref_value = int(values[0])
        if alt_value >= 0:
            split_read_alt = alt_value
        if ref_value >= 0:
            split_read_ref = ref_value

    # Number of paired ends that supports the event
    if "DV" in variant.FORMAT:
        values = variant.format("DV")[pos]
        alt_value = int(values[0])
        if alt_value >= 0:
            paired_end_alt = alt_value

    # Number of paired ends that supports the reference
    if "DR" in variant.FORMAT:
        values = variant.format("DR")[pos]
        ref_value = int(values[0])
        if alt_value >= 0:
            paired_end_ref = ref_value

    # Number of split reads that supports the event
    if "RV" in variant.FORMAT:
        values = variant.format("RV")[pos]
        alt_value = int(values[0])
        if alt_value >= 0:
            split_read_alt = alt_value

    # Number of split reads that supports the reference
    if "RR" in variant.FORMAT:
        values = variant.format("RR")[pos]
        ref_value = int(values[0])
        if ref_value >= 0:
            split_read_ref = ref_value

    alt_depth = int(variant.gt_alt_depths[pos])
    if alt_depth == -1:
        if "VD" in variant.FORMAT:
            alt_depth = int(variant.format("VD")[pos][0])

        if any([paired_end_alt, split_read_alt]):
            alt_depth = 0
            if paired_end_alt:
                alt_depth += paired_end_alt
            if split_read_alt:
                alt_depth += split_read_alt

        if any([spanning_alt, flanking_alt, inrepeat_alt]):
            alt_depth = 0
            if spanning_alt:
                alt_depth += spanning_alt
            if flanking_alt:
                alt_depth += flanking_alt
            if inrepeat_alt:
                alt_depth += inrepeat_alt

    gt_call["alt_depth"] = alt_depth

    ref_depth = int(variant.gt_ref_depths[pos])
    if ref_depth == -1:
        if any([paired_end_ref, split_read_ref]):
            ref_depth = 0
            if paired_end_ref:
                ref_depth += paired_end_ref
            if split_read_ref:
                ref_depth += split_read_ref

        if any([spanning_ref, flanking_ref, inrepeat_ref]):
            ref_depth = 0
            if spanning_ref:
                ref_depth += spanning_ref
            if flanking_ref:
                ref_depth += flanking_ref
            if inrepeat_ref:
                ref_depth += inrepeat_ref

    gt_call["ref_depth"] = ref_depth

    alt_frequency = float(variant.gt_alt_freqs[pos])
    if alt_frequency == -1:
        if "AF" in variant.FORMAT:
            alt_frequency = float(variant.format("AF")[pos][0])

    read_depth = int(variant.gt_depths[pos])
    if read_depth == -1:
        # If read depth could not be parsed by cyvcf2, try to get it manually
        if "DP" in variant.FORMAT:
            read_depth = int(variant.format("DP")[pos][0])
        elif "LC" in variant.FORMAT:
            value = variant.format("LC")[pos][0]
            try:
                read_depth = int(round(value))
            except ValueError as e:
                pass
        elif alt_depth != -1 or ref_depth != -1:
            read_depth = 0
            if alt_depth != -1:
                read_depth += alt_depth
            if ref_depth != -1:
                read_depth += alt_depth

    gt_call["read_depth"] = read_depth

    gt_call["alt_frequency"] = alt_frequency

    gt_call["genotype_quality"] = int(variant.gt_quals[pos])

    return gt_call


def _parse_format_entry(variant, pos, format_entry_name):
    """Parse genotype format entry for named integer values.
    Expects that ref/alt values could be separated by /.

    Args:
        variant(cyvcf2.Variant)
        pos(int): individual position in VCF
        format_entry_name: name of format entry
    Returns:
        (ref(int), alt(int)) tuple
    """

    ref = None
    alt = None
    if format_entry_name in variant.FORMAT:
        try:
            value = variant.format(format_entry_name)[pos]
            values = list(value.split("/"))

            ref_value = None
            alt_value = None

            if len(values) > 1:
                ref_value = int(values[0])
                alt_value = int(values[1])
            if len(values) == 1:
                alt_value = int(values[0])
            if ref_value >= 0:
                ref = ref_value
            if alt_value >= 0:
                alt = alt_value
        except (ValueError, TypeError) as e:
            pass
    return (ref, alt)
