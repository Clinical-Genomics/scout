from scout.parse.variant.coordinates import (get_cytoband_coordinates, get_sub_category, 
                                             get_length, get_end, parse_coordinates)


class CyvcfVariant(object):
    """Mock a cyvcf variant
    
    Default is to return a variant with three individuals high genotype 
    quality.
    """
    def __init__(self, chrom='1', pos=80000, ref='A', alt='C', end=None, 
                 gt_quals=[60, 60, 60], gt_types=[1, 1, 0], var_type='snv',
                 info_dict={}):
        super(CyvcfVariant, self).__init__()
        self.CHROM = chrom
        self.POS = pos
        self.REF = ref
        self.ALT = [alt]
        self.end = end or pos
        self.gt_quals = gt_quals
        self.gt_types = gt_types
        self.var_type = var_type
        self.INFO = info_dict


def test_parse_coordinates_snv():
    variant = CyvcfVariant()
    
    coordinates = parse_coordinates(variant, 'snv')
    
    assert coordinates['position'] == variant.POS

def test_parse_coordinates_indel():
    variant = CyvcfVariant(alt='ACCC', end=80003)
    
    coordinates = parse_coordinates(variant, 'snv')
    
    assert coordinates['position'] == variant.POS
    assert coordinates['end'] == variant.end

def test_parse_coordinates_translocation():
    info_dict = {
        'SVTYPE': 'BND',
    }
    variant = CyvcfVariant(
        ref='N', 
        alt='N[hs37d5:12060532[',
        pos=724779,
        end=724779,
        var_type='sv',
        info_dict=info_dict,
    )
    
    coordinates = parse_coordinates(variant, 'sv')
    
    assert coordinates['position'] == variant.POS
    assert coordinates['end'] == 12060532
    assert coordinates['end_chrom'] == 'hs37d5'
    assert coordinates['length'] == 10e10
    assert coordinates['sub_category'] ==  'bnd'

def test_parse_coordinates_translocation_2():
    info_dict = {
        'SVTYPE': 'BND',
    }
    variant = CyvcfVariant(
        ref='N', 
        alt='N[GL000232.1:25141[',
        pos=724779,
        end=724779,
        var_type='sv',
        info_dict=info_dict,
    )
    
    coordinates = parse_coordinates(variant, 'sv')
    
    assert coordinates['position'] == variant.POS
    assert coordinates['end'] == 25141
    assert coordinates['end_chrom'] == 'GL000232.1'
    assert coordinates['length'] == 10e10
    assert coordinates['sub_category'] ==  'bnd'
    
    
###### parse subcategory #######
def test_get_subcategory_snv():
    alt_len = 1
    ref_len = 1
    category = 'snv'
    svtype = None
    
    sub_category = get_sub_category(alt_len, ref_len, category, svtype)
    
    assert sub_category == 'snv'

def test_get_subcategory_indel():
    alt_len = 1
    ref_len = 3
    category = 'snv'
    svtype = None
    
    sub_category = get_sub_category(alt_len, ref_len, category, svtype)
    
    assert sub_category == 'indel'

###### parse length #######

# get_length(alt_len, ref_len, category, pos, end, svtype=None, svlen=None)
def test_get_length_snv():
    alt_len = 1
    ref_len = 1
    category = 'snv'
    pos = end = 879537
    
    length = get_length(alt_len, ref_len, category, pos, end)
    
    assert length == 1

def test_get_length_indel():
    alt_len = 3
    ref_len = 1
    category = 'snv'
    pos = end = 879537
    
    length = get_length(alt_len, ref_len, category, pos, end)
    
    assert length == 2

def test_get_sv_length_small_ins():
    ## GIVEN an insertion with whole sequence in alt field
    alt_len = 296
    ref_len = 1
    category = 'sv'
    # Pos and end is same for insertions
    pos = end = 144343218
    svtype = 'ins'
    svlen = 296
    
    ## WHEN parsing the length
    length = get_length(alt_len, ref_len, category, pos, end, svtype, svlen)
    
    ## THEN assert that the length is correct
    assert length == 296

def test_get_sv_length_large_ins_no_length():
    ## GIVEN an imprecise insertion
    alt_len = 5
    ref_len = 1
    category = 'sv'
    # Pos and end is same for insertions
    pos = end = 133920667
    svtype = 'ins'
    svlen = None
    
    ## WHEN parsing the length
    length = get_length(alt_len, ref_len, category, pos, end, svtype, svlen)
    
    ## THEN assert that the length is correct
    assert length == -1

def test_get_sv_length_translocation():
    ## GIVEN an translocation
    alt_len = 16
    ref_len = 1
    category = 'sv'
    pos = 726044
    end = None
    svtype = 'bnd'
    svlen = None
    
    ## WHEN parsing the length
    length = get_length(alt_len, ref_len, category, pos, end, svtype, svlen)
    
    ## THEN assert that the length is correct
    assert length == 10e10

def test_get_sv_length_cnvnator_del():
    ## GIVEN an cnvnator type deletion
    alt_len = 5
    ref_len = 1
    category = 'sv'
    pos = 1
    end = 10000
    svtype = 'del'
    svlen = -10000
    
    ## WHEN parsing the length
    length = get_length(alt_len, ref_len, category, pos, end, svtype, svlen)
    
    ## THEN assert that the length is correct
    assert length == 10000

def test_get_sv_length_del_no_length():
    ## GIVEN an deletion without len
    alt_len = 5
    ref_len = 1
    category = 'sv'
    pos = 869314
    end = 870246
    svtype = 'del'
    svlen = None
    
    ## WHEN parsing the length
    length = get_length(alt_len, ref_len, category, pos, end, svtype, svlen)
    
    ## THEN assert that the length is correct
    assert length == end - pos

###### parse end #######
# get_end(pos, alt, category, snvend, svend, svlen)

# snv/indels are easy since cyvcf2 are parsing the end for us

def test_get_end_snv():
    alt = 'T'
    category = 'snv'
    pos = snvend = 879537
    
    end = get_end(pos, alt, category, snvend, svend=None, svlen=None)
    
    assert end == snvend

def test_get_end_indel():
    alt = 'C'
    category = 'indel'
    pos = 302253
    snvend = 302265
    
    end = get_end(pos, alt, category, snvend, svend=None, svlen=None)
    
    assert end == snvend

# SVs are much harder since there are a lot of corner cases
# Most SVs (except translocations) have END annotated in INFO field
# The problem is that many times END==POS and then we have to do some magic on our own

def test_get_end_tiddit_translocation():
    ## GIVEN a translocation
    alt = 'N[hs37d5:12060532['
    category = 'sv'
    pos = 724779
    
    ## WHEN parsing the end coordinate
    end = get_end(pos, alt, category, snvend=None, svend=None, svlen=None)
    
    ## THEN assert that the end is the same as en coordinate described in alt field
    assert end == 12060532

def test_get_end_tiddit_translocation():
    ## GIVEN a translocation
    alt = 'N[hs37d5:12060532['
    category = 'sv'
    pos = 724779
    
    ## WHEN parsing the end coordinate
    end = get_end(pos, alt, category, snvend=None, svend=None, svlen=None)
    
    ## THEN assert that the end is the same as en coordinate described in alt field
    assert end == 12060532

def test_get_end_deletion():
    ## GIVEN a translocation
    alt = '<DEL>'
    category = 'sv'
    pos = 869314
    svend = 870246
    svlen = None
    
    ## WHEN parsing the end coordinate
    end = get_end(pos, alt, category, snvend=None, svend=svend, svlen=svlen)
    
    ## THEN assert that the end is the same as en coordinate described in alt field
    assert end == svend


