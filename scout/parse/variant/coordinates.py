from scout.constants import (CYTOBANDS, BND_ALT_PATTERN, CHR_PATTERN)

def get_cytoband_coordinates(chrom, pos):
    """Get the cytoband coordinate for a position

    Args:
        chrom(str)
        pos(int)

    Returns:
        coordinate(str)
    """
    coordinate = ""

    if chrom in CYTOBANDS:
        for interval in CYTOBANDS[chrom][pos]:
            coordinate = interval.data

    return coordinate

def get_sub_category(alt_len, ref_len, category, svtype=None):
    """Get the subcategory for a VCF variant

    The sub categories are:
        'snv', 'indel', 'del', 'ins', 'dup', 'bnd', 'inv'

    Args:
        alt_len(int)
        ref_len(int)
        category(str)
        svtype(str)

    Returns:
        subcategory(str)
    """
    subcategory = ''

    if category in ('snv', 'indel', 'cancer'):
        if ref_len == alt_len:
            subcategory = 'snv'
        else:
            subcategory = 'indel'
    elif category == 'sv':
        subcategory = svtype

    return subcategory

def get_length(alt_len, ref_len, category, pos, end, svtype=None, svlen=None):
    """Return the length of a variant

    Args:
        alt_len(int)
        ref_len(int)
        category(str)
        svtype(str)
        svlen(int)
    """
    # -1 would indicate uncertain length
    length = -1
    if category in ('snv', 'indel', 'cancer'):
        if ref_len == alt_len:
            length = alt_len
        else:
            length = abs(ref_len - alt_len)

    elif category == 'sv':
        if svtype == 'bnd':
            length = int(10e10)
        else:
            if svlen:
                length = abs(int(svlen))
            # Some software does not give a length but they give END
            elif end:
                if end != pos:
                    length = end - pos
    return length

def get_end(pos, alt, category, snvend=None, svend=None, svlen=None):
    """Return the end coordinate for a variant

    Args:
        pos(int)
        alt(str)
        category(str)
        snvend(str)
        svend(int)
        svlen(int)

    Returns:
        end(int)
    """
    # If nothing is known we set end to be same as start
    end = pos
    # If variant is snv or indel we know that cyvcf2 can handle end pos
    if category in ('snv', 'indel', 'cancer'):
        end = snvend

    # With SVs we have to be a bit more careful
    elif category == 'sv':
        # The END field from INFO usually works fine
        end = svend

        # For some cases like insertions the callers set end to same as pos
        # In those cases we can hope that there is a svlen...
        if svend == pos:
            if svlen:
                end = pos + svlen
        # If variant is 'BND' they have ':' in alt field
        # Information about other end is in the alt field
        if ':' in alt:
            match = BND_ALT_PATTERN.match(alt)
            if match:
                end = int(match.group(2))

    return end

def parse_coordinates(variant, category):
    """Find out the coordinates for a variant

    Args:
        variant(cyvcf2.Variant)

    Returns:
        coordinates(dict): A dictionary on the form:
        {
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
    ref = variant.REF

    if variant.ALT:
        alt = variant.ALT[0]
    if category=="str" and not variant.ALT:
        alt = '.'

    chrom_match = CHR_PATTERN.match(variant.CHROM)
    chrom = chrom_match.group(2)

    svtype = variant.INFO.get('SVTYPE')
    if svtype:
        svtype = svtype.lower()

    mate_id = variant.INFO.get('MATEID')

    svlen = variant.INFO.get('SVLEN')

    svend = variant.INFO.get('END')
    snvend = int(variant.end)

    position = int(variant.POS)

    ref_len = len(ref)
    alt_len = len(alt)

    sub_category = get_sub_category(alt_len, ref_len, category, svtype)
    end = get_end(position, alt, category, snvend, svend)

    length = get_length(alt_len, ref_len, category, position, end, svtype, svlen)
    end_chrom = chrom

    if sub_category == 'bnd':
        if ':' in alt:
            match = BND_ALT_PATTERN.match(alt)
            # BND will often be translocations between different chromosomes
            if match:
                other_chrom = match.group(1)
                match = CHR_PATTERN.match(other_chrom)
                end_chrom = match.group(2)

    cytoband_start = get_cytoband_coordinates(chrom, position)
    cytoband_end = get_cytoband_coordinates(end_chrom, end)

    coordinates = {
        'position': position,
        'end': end,
        'length': length,
        'sub_category': sub_category,
        'mate_id': mate_id,
        'cytoband_start': cytoband_start,
        'cytoband_end': cytoband_end,
        'end_chrom': end_chrom,
    }


    return coordinates
