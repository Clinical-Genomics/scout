"""Code to parse variant coordinates"""

from scout.constants import BND_ALT_PATTERN, CHR_PATTERN, CYTOBANDS_37, CYTOBANDS_38


def get_cytoband_coordinates(chrom, pos, build):
    """Get the cytoband coordinate for a position

    Args:
        chrom(str)
        pos(int)
        build(str)

    Returns:
        coordinate(str)
    """
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


def sv_length(pos, end, chrom, end_chrom, svlen=None):
    """Return the length of a structural variant

    Args:
        pos(int)
        end(int)
        chrom(str)
        end_chrom(str)
        svlen(int)

    Returns:
        length(int)
    """
    if chrom != end_chrom:
        return int(10e10)
    if svlen:
        return abs(int(svlen))
    # Some software does not give a length but they give END
    if not end:
        return -1

    if end == pos:
        return -1

    return end - pos


def sv_end(pos: int, alt: str, svend: int = None, svlen: int = None) -> int:
    """Return the end coordinate for a structural variant
    The END field from INFO usually works fine, although for some cases like insertions the callers
     set end to same as pos. In those cases we can hope that there is a svlen...

    Translocations needs their own treatment as usual
    """
    end = svend

    if ":" in alt:
        match = BND_ALT_PATTERN.match(alt)
        if match:
            end = int(match.group(2))

    if end is None and svlen:
        end = pos + svlen

    return end


def get_end_chrom(alt, chrom):
    """Return the end chromosome for a tranlocation

    Args:
        alt(str)
        chrom(str)

    Returns:
        end_chrom(str)
    """
    end_chrom = chrom
    if ":" not in alt:
        return end_chrom

    match = BND_ALT_PATTERN.match(alt)
    # BND will often be translocations between different chromosomes
    if match:
        other_chrom = match.group(1)
        match = CHR_PATTERN.match(other_chrom)
        end_chrom = match.group(2)
    return end_chrom


def parse_coordinates(variant, category, build="37"):
    """Find out the coordinates for a variant

    Args:
        variant(cyvcf2.Variant)
        category(str): snv, sv, str, cancer, cancer_sv
        build(str): "37" or "38"

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

    if category in ["sv", "cancer_sv", "fusion"]:
        svtype = variant.INFO.get("SVTYPE")
        if svtype:
            svtype = svtype.lower()
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
    elif category == "mei":
        sub_category = "mei"
        end = int(variant.end)
        length = alt_len
        if ref_len != alt_len:
            sub_category = "mei"
            length = abs(ref_len - alt_len)
    else:
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
