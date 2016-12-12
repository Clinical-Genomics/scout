
def parse_coordinates(ref, alt, position, category, svtype, svlen, end, mate_id=None):
    """Find out the coordinates for a variant
    
        Args:
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
        'end': None,
        'length': None,
        'sub_category': None,
        'mate_id':None,
    }
    if category == 'snv':
        ref_len = len(ref)
        alt_len = len(alt)
        # If lenth is same lenth is same as alternative
        if ref_len == alt_len:
            coordinates['length'] = alt_len
            coordinates['end'] = position + (alt_len -1)
            if alt_len == 1:
                coordinates['sub_category'] = 'snv'
            else:
                coordinates['sub_category'] = 'indel'
        # Ref > Alt we have an deletion
        elif ref_len > alt_len:
            coordinates['length'] = ref_len - alt_len
            coordinates['end'] = position + (ref_len - 1)
            coordinates['sub_category'] = 'indel'
        # Alt > Ref we have an insertion
        elif ref_len < alt_len:
            coordinates['length'] = alt_len - ref_len
            coordinates['end'] = position + (alt_len - 1)
            coordinates['sub_category'] = 'indel'

    elif category == 'sv':
        if svtype:
            coordinates['sub_category'] = svtype
        else:
            raise VcfError("SVs has to have SVTYPE")
        
        if coordinates['sub_category'] == 'bnd':
            if mate_id:
                coordinates['mate_id'] = mate_id
            #For translocations we set lenth to infinity
            coordinates['length'] = int(10e10)
            coordinates['end'] = int(10e10)
        else:
            if svlen:
                coordinates['length'] = abs(int(svlen))
            else:
                # -1 would indicate uncertain length
                coordinates['length'] = -1
            
            coordinates['end'] = int(end)

    return coordinates
