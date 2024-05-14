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

import logging
from typing import Dict, List, Optional, Tuple, Union

import cyvcf2

GENOTYPE_MAP = {0: "0", 1: "1", -1: "."}
LOG = logging.getLogger(__name__)


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

    MEI specific format fields
    ##FORMAT=<ID=CLIP3,Number=1,Type=Float,Description="Number of soft clipped reads downstream of the breakpoint">
    ##FORMAT=<ID=CLIP5,Number=1,Type=Float,Description="Number of soft clipped reads upstream of the breakpoint">
    ##FORMAT=<ID=SP,Number=1,Type=Float,Description="Number of correctly mapped read pairs spanning breakpoint, useful for estimation of size of insertion">
    ##FORMAT=<ID=SP,Number=1,Type=Float,Description="Number of correctly mapped read pairs spanning breakpoint, useful for estimation of size of insertion">

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
    gt_call["so"] = get_str_so(variant, pos)

    (spanning_ref, spanning_alt) = _parse_format_entry(variant, pos, "ADSP")
    (flanking_ref, flanking_alt) = _parse_format_entry(variant, pos, "ADFL")
    (inrepeat_ref, inrepeat_alt) = _parse_format_entry(variant, pos, "ADIR")

    # TRGT long read STR specific
    (_, mc_alt) = _parse_format_entry_trgt_mc(variant, pos)
    gt_call["alt_mc"] = mc_alt

    (sd_ref, sd_alt) = _parse_format_entry(variant, pos, "SD", float)
    (ap_ref, ap_alt) = _parse_format_entry(variant, pos, "AP", float)
    (am_ref, am_alt) = _parse_format_entry(variant, pos, "AM", float)

    # MEI specific
    (spanning_mei_ref, clip5_alt, clip3_alt) = get_mei_reads(
        variant, pos
    )  # allowing mei SP to override STR ADSP for spanning

    # SV specific
    (paired_end_ref, paired_end_alt) = get_paired_ends(variant, pos)
    (split_read_ref, split_read_alt) = get_split_reads(variant, pos)

    alt_depth = get_alt_depth(
        variant,
        pos,
        paired_end_alt,
        split_read_alt,
        spanning_alt,
        flanking_alt,
        inrepeat_alt,
        clip5_alt,
        clip3_alt,
    )
    gt_call["alt_depth"] = alt_depth

    ref_depth = get_ref_depth(
        variant,
        pos,
        paired_end_ref,
        split_read_ref,
        spanning_ref,
        flanking_ref,
        inrepeat_ref,
        spanning_mei_ref,
    )
    gt_call["ref_depth"] = ref_depth
    gt_call["read_depth"] = get_read_depth(variant, pos, alt_depth, ref_depth)
    gt_call["alt_frequency"] = get_alt_frequency(variant, pos)
    gt_call["genotype_quality"] = int(variant.gt_quals[pos])
    gt_call["ffpm"] = get_ffpm_info(variant, pos)
    gt_call["split_read"] = split_read_alt

    return gt_call


def get_mei_reads(variant: cyvcf2.Variant, pos: Dict[str, int]) -> Tuple[int, ...]:
    """Get MEI caller read details from FORMAT tags.
    Returns:
        tuple(int, int, int) spanning_ref, clip5p_alt, clip3p_alt
    """
    spanning_ref = None
    clip5_alt = None
    clip3_alt = None

    # Number of (reference) variant spanning reads
    if "SP" in variant.FORMAT:
        try:
            values = variant.format("SP")[pos]
            ref_value = int(values[0])
            if ref_value >= 0:
                spanning_ref = ref_value
        except ValueError as _ignore_error:
            pass

    # Number of split reads upstream (supporting alt)
    if "CLIP5" in variant.FORMAT:
        try:
            values = variant.format("CLIP5")[pos]
            alt_value = int(values[0])
            if alt_value >= 0:
                clip5_alt = alt_value
        except ValueError as _ignore_error:
            pass

    if "CLIP3" in variant.FORMAT:
        try:
            values = variant.format("CLIP3")[pos]
            alt_value = int(values[0])
            if alt_value >= 0:
                clip3_alt = alt_value
        except ValueError as _ignore_error:
            pass

    return (spanning_ref, clip5_alt, clip3_alt)


def get_ffpm_info(variant: cyvcf2.Variant, pos: Dict[str, int]) -> Optional[int]:
    """Get FUSION caller read details from FORMAT tags.
    Returns:
        tuple(int, int, int) supporting_reads, split_reads, ffpm
    """
    # Fusion fragments per million total RNA-seq fragments
    if "FFPM" in variant.FORMAT:
        try:
            values = variant.format("FFPM")[pos]
            return int(values[0])
        except ValueError as _ignore_error:
            pass


def get_paired_ends(variant, pos):
    """Get paired ends"""
    # SV specific
    paired_end_alt = None
    paired_end_ref = None

    # Check if PE is annotated
    # This is the number of paired end reads that supports the variant
    if "PE" in variant.FORMAT:
        try:
            value = int(variant.format("PE")[pos])
            if value >= 0:
                paired_end_alt = value
        except ValueError as _ignore_error:
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
        except ValueError as _ignore_error:
            pass

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
        if ref_value >= 0:
            paired_end_ref = ref_value
    return (paired_end_ref, paired_end_alt)


def get_split_reads(variant, pos):
    """Get split reads"""
    split_read_alt = None
    split_read_ref = None
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

    return (split_read_ref, split_read_alt)


def get_alt_frequency(variant, pos):
    """ """
    alt_frequency = float(variant.gt_alt_freqs[pos])
    if alt_frequency == -1:
        if "AF" in variant.FORMAT:
            alt_frequency = float(variant.format("AF")[pos][0])
    return alt_frequency


def get_read_depth(variant, pos, alt_depth, ref_depth):
    """Read depth"""
    read_depth = int(variant.gt_depths[pos])
    if read_depth == -1:
        # If read depth could not be parsed by cyvcf2, try to get it manually
        if "DP" in variant.FORMAT:
            read_depth = int(variant.format("DP")[pos][0])
        elif "LC" in variant.FORMAT:
            value = variant.format("LC")[pos][0]
            try:
                read_depth = int(round(value))
            except ValueError as _ignore_error:
                pass
        elif alt_depth != -1 or ref_depth != -1:
            read_depth = 0
            if alt_depth != -1:
                read_depth += alt_depth
            if ref_depth != -1:
                read_depth += alt_depth
    return read_depth


def get_ref_depth(
    variant,
    pos,
    paired_end_ref,
    split_read_ref,
    spanning_ref,
    flanking_ref,
    inrepeat_ref,
    spanning_mei_ref,
):
    """Get reference read depth"""
    ref_depth = int(variant.gt_ref_depths[pos])
    if ref_depth != -1:
        return ref_depth

    REF_ITEMS_LIST: List[tuple] = [
        (paired_end_ref, split_read_ref),
        (spanning_ref, flanking_ref, inrepeat_ref),
    ]

    for list in REF_ITEMS_LIST:
        if all(item is None for item in list):
            continue
        ref_depth = 0
        for item in list:
            if item:
                ref_depth += item

    if spanning_mei_ref:
        ref_depth += spanning_mei_ref
    return ref_depth


def get_alt_depth(
    variant,
    pos,
    paired_end_alt,
    split_read_alt,
    spanning_alt,
    flanking_alt,
    inrepeat_alt,
    clip5_alt,
    clip3_alt,
):
    """Get alternative read depth"""
    alt_depth = int(variant.gt_alt_depths[pos])
    if alt_depth != -1:
        return alt_depth

    if "VD" in variant.FORMAT:
        alt_depth = int(variant.format("VD")[pos][0])

    ALT_ITEMS_LIST: List[tuple] = [
        (paired_end_alt, split_read_alt),
        (clip5_alt, clip3_alt),
        (spanning_alt, flanking_alt, inrepeat_alt),
    ]

    for list in ALT_ITEMS_LIST:
        if all(item is None for item in list):
            continue
        alt_depth = 0
        for item in list:
            if item:
                alt_depth += item

    return alt_depth


def get_str_so(variant, pos):
    """Get str SO from variant"""
    str_so = None
    if "SO" in variant.FORMAT:
        try:
            so = variant.format("SO")[pos]
            if so not in [None, -1]:
                str_so = str(so)
        except ValueError as _ignore_error:
            pass
    return str_so


def split_values(values: List[str]) -> List[str]:
    """
    Expects that ref/alt values could be separated by "/" or ",".

    """
    new_values = []
    for value in values:
        for delim in ["/", ","]:
            if delim in value:
                new_values = list(value.split(delim))

    if new_values:
        return new_values

    return values


def _parse_format_entry(
    variant: cyvcf2.Variant,
    pos: int,
    format_entry_name: str,
    number_format: Optional[Union[float, int]] = int,
) -> Tuple[Union[float, int], ...]:
    """Parse genotype format entry for named integer values.
    Expects that ref/alt values could be separated by "/" or ",".
    Give individual position in VCF as pos and name of format entry to parse as format_entry_name.
    """

    ref = None
    alt = None
    if format_entry_name in variant.FORMAT:
        try:
            values = split_values(variant.format(format_entry_name)[pos])

            ref_value = None
            alt_value = None

            if len(values) > 1:
                ref_value = (number_format)(values[0])
                alt_value = (number_format)(values[1])
            if len(values) == 1:
                alt_value = (number_format)(values[0])
            if ref_value >= 0:
                ref = ref_value
            if alt_value >= 0:
                alt = alt_value
        except (ValueError, TypeError) as _ignore_error:
            pass
    return (ref, alt)


def _parse_format_entry_trgt_mc(variant: cyvcf2.Variant, pos: int):
    """Parse genotype entry for TRGT FORMAT MC

    The MC format contains the Motif Counts for each allele, separated with "," and each motif in an expansion,
    as a "_" separated list of the different available enumerated motifs. For some loci,
    only certain motifs count towards a pathologic size, and if so a PathologicStruc INFO key is passed.
    E.g. for non-reference motifs and more complex loci or alleles with different motifs.
    As usual, VCF lines are decomposed, so at most one alt is present per entry.
    The GT position gives us a ref index for any allele 0 in the call.
    """

    mc_ref = None
    mc_alt = None

    if "MC" not in variant.FORMAT:
        return (mc_ref, mc_alt)

    mc = variant.format("MC")[pos]
    if not mc:
        return (mc_ref, mc_alt)

    ref_idx = None
    gt = variant.genotypes[pos]
    if gt:
        for idx, allele in enumerate(gt):
            if allele == 0:
                ref_idx = idx

    pathologic_struc = variant.INFO.get("PathologicStruc", None)
    pathologic_counts = 0
    for idx, allele in enumerate(mc.split(",")):
        mcs = allele.split("_")

        if len(mcs) > 1:
            pathologic_mcs = pathologic_struc or range(len(mcs))

            for index, count in enumerate(mcs):
                if index in pathologic_mcs:
                    pathologic_counts += int(count)
        else:
            pathologic_counts = int(allele)

        if ref_idx is not None and idx == ref_idx:
            mc_ref = pathologic_counts
            continue

        mc_alt = pathologic_counts

    return (mc_ref, mc_alt)
