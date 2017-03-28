
def build_clnsig(clnsig_info):
    """docstring for build_clnsig"""
    clnsig_obj = dict(
        value = clnsig_info['value'],
        accession = clnsig_info['accession'],
        revstat = clnsig_info['revstat']
    )
    
    return clnsig_obj