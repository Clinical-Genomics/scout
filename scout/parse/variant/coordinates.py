from scout.constants import CYTOBANDS

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
    """Get the subcategory"""
    subcategory = ''
    
    if category in ('snv', 'indel', 'cancer'):
        if ref_len == alt_len:
            subcategory = 'snv'
        else:
            subcategory = 'indel'
    elif category == 'sv':
        subcategory = svtype
    
    return subcategory

def get_length(alt_len, ref_len, category, svtype=None, svlen=None):
    """docstring for get_length"""
    if category in ('snv', 'indel', 'cancer'):
        if ref_len == alt_len:
            length = alt_len
        else:
            length = abs(ref_len-alt_len)
    elif category == 'sv':
        if svtype == 'bnd':
            length = int(10e10)
        else:
            if svlen:
                length = abs(int(svlen))
            else:
                # -1 would indicate uncertain length
                length = -1
    return length

def get_end(pos, length, alt, category, svtype=None):
    """docstring for get_length"""
    end = None
    if category in ('snv', 'indel', 'cancer'):
        end = pos + length

    elif category == 'sv':
        if ':' in alt:
            other_coordinates = alt.strip('ACGTN[]').split(':')
            # For BND end will represent the end position of the other end
            try:
                end = int(other_coordinates[1])
            except ValueError as err:
                end = pos + length
        else:
            end = pos + length
    
    return end


def parse_coordinates(chrom, ref, alt, position, category, svtype, svlen, end, mate_id=None):
    """Find out the coordinates for a variant
    
    Args:
        chrom(str)
        ref(str)
        alt(str)
        position(int)
        category(str)
        svtype(str)
        svlen(int)
        end(int)
        mate_id(str)
    
    Returns:
        coordinates(dict): A dictionary on the form:
        {
            'end':<int>, 
            'length':<int>, 
            'sub_category':<str>,
            'mate_id':<str>,
        }
    """
    coordinates = {
        'end': end,
        'length': None,
        'sub_category': None,
        'mate_id':None,
        'cytoband_start':None,
        'cytoband_end':None,
        'end_chrom':None,
    }
    if svtype:
        svtype = svtype.lower()

    ref_len = len(ref)
    alt_len = len(alt)
    coordinates['mate_id'] = mate_id
    coordinates['sub_category'] = get_sub_category(alt_len, ref_len, category, svtype)
    coordinates['length'] = get_length(alt_len, ref_len, category, svtype, svlen)
    coordinates['end'] = get_end(position, coordinates['length'], alt, category, svtype)
    coordinates['end_chrom'] = chrom

    if coordinates['sub_category'] == 'bnd':    
            if ':' in alt:
                other_coordinates = alt.strip('ACGTN[]').split(':')
                # BND will often be translocations between different chromosomes
                other_chrom = other_coordinates[0]
                coordinates['end_chrom'] = other_coordinates[0].lstrip('chrCHR')
    
    coordinates['cytoband_start'] = get_cytoband_coordinates(
        chrom, position
    )
    coordinates['cytoband_end'] = get_cytoband_coordinates(
        coordinates['end_chrom'], coordinates['end']
    )

    return coordinates
