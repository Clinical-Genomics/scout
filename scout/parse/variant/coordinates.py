"""Code to parse variant coordinates"""

import cyvcf2

from scout.constants import BND_ALT_PATTERN, CHR_PATTERN, CYTOBANDS_37, CYTOBANDS_38, SV_TYPES


def get_cytoband_coordinates(chrom: str, pos: int, build: str) -> str:
    """Get the cytoband coordinate for a position"""
    coordinate = ""

    if "38" in str(build):
        coord_resource = CYTOBANDS_38
    else:
        coord_resource = CYTOBANDS_37

    if chrom not in coord_resource:
        return coordinate

    for interval in coord_resource[chrom][pos]:
        coordinate = interval.data

    return coordinate


def sv_length(
    pos: int, end: int | None, chrom: str, end_chrom: str, svlen: int | None = None
) -> int:
    """Return the length of a structural variant

    Return inf-like number if on different molecules. Use svlen if available.

    Some software does not give a length, but they (or cyvcf2) give END

    end identical to POS gives length -1, as does a missing end.
    """
    if chrom != end_chrom:
        return int(10e10)
    if svlen:
        return abs(int(svlen))

    if not end:
        return -1

    if end == pos:
        return -1

    return end - pos


def sv_end(pos: int, alt: str, svend: int | None = None, svlen: int | None = None) -> int:
    """Return the end coordinate for a structural variant
    The END field from INFO usually works fine, although for some cases like insertions the callers
     set end to same as pos. In those cases we can hope that there is a svlen..

    Translocations need their own treatment, setting end based on the info in the ALT allele pattern.

    Single end BNDs by definition have no real end, and get END set to POS.
    """
    end = svend

    if ":" in alt:
        if match := BND_ALT_PATTERN.match(alt):
            end = int(match.group(2))
    elif "." in alt and len(alt) > 1:
        end = pos

    if end is None and svlen:
        end = pos + svlen

    return end


def get_end_chrom(alt: str, chrom: str) -> str:
    """Return the end chromosome for a translocation

    BND will often be translocations between different chromosomes
    """
    end_chrom = chrom
    if ":" not in alt:
        return end_chrom

    if match := BND_ALT_PATTERN.match(alt):
        other_chrom = match.group(1)
        match = CHR_PATTERN.match(other_chrom)
        end_chrom = match.group(2)
    return end_chrom


def get_svtype(variant: cyvcf2.Variant, alt: str, alt_len: int) -> str:
    """Find SV type for structural variants. The INFO tag has been deprecated in the VCF standard,
    but not removed. If it is still there we can use it."""
    svtype = variant.INFO.get("SVTYPE")
    if svtype:
        svtype = svtype.lower()
        if svtype == "sgl":
            svtype = "bnd"
    else:
        alt_type = alt.lstrip("<").rstrip(">").lower()
        if alt_type in SV_TYPES:
            svtype = alt_type
        elif "." in alt and alt_len > 1:
            svtype = "bnd"
    return svtype


def parse_coordinates(variant: cyvcf2.Variant, category: str, build: str = "37") -> dict:
    """Find out the coordinates for a variant

    Returns:
        coordinates(dict): A dictionary on the form:
        {
            'chrom':<str>,
            'ref':<str>,
            'alt':<str>,
            'position':<int>,
            'end':<int>,
            'end_chrom':<str>,
            'length':<int>,
            'sub_category':<str>,
            'mate_id':<str>,
            'cytoband_start':<str>,
            'cytoband_end':<str>,
        }
    """
    alt = None
    if variant.ALT:
        alt = variant.ALT[0]
    elif category == "str" and not variant.ALT:
        alt = "."
    alt_len = len(alt)

    chrom_match = CHR_PATTERN.match(variant.CHROM)
    chrom = chrom_match.group(2)
    end_chrom = chrom

    position = int(variant.POS)

    ref = variant.REF
    ref_len = len(ref)

    match category:
        case "sv" | "cancer_sv" | "fusion":
            svtype = get_svtype(variant, alt, alt_len)

            sub_category = svtype
            if sub_category == "bnd":
                end_chrom = get_end_chrom(alt, chrom)
            end = sv_end(
                pos=position,
                alt=alt,
                svend=variant.INFO.get("END"),
                svlen=variant.INFO.get("SVLEN"),
            )
            length = sv_length(
                pos=position,
                end=end,
                chrom=chrom,
                end_chrom=end_chrom,
                svlen=variant.INFO.get("SVLEN"),
            )
        case "mei":
            sub_category = "mei"
            end = int(variant.end)
            length = alt_len
            if ref_len != alt_len:
                sub_category = "mei"
                length = abs(ref_len - alt_len)
        case _:
            sub_category = "snv"
            end = int(variant.end)
            length = alt_len
            if ref_len != alt_len:
                sub_category = "indel"
                length = abs(ref_len - alt_len)

    coordinates = {
        "chrom": chrom,
        "position": position,
        "ref": ref,
        "alt": alt,
        "end": end,
        "length": length,
        "sub_category": sub_category,
        "mate_id": variant.INFO.get("MATEID"),
        "cytoband_start": get_cytoband_coordinates(chrom, position, build),
        "cytoband_end": get_cytoband_coordinates(end_chrom, end, build),
        "end_chrom": end_chrom,
    }

    return coordinates
