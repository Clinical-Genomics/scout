from scout.parse.ids import (parse_ids, parse_simple_id, parse_variant_id,
                             parse_display_name, parse_document_id)

from scout.utils.md5 import generate_md5_key

def test_parse_simple_id():
    chrom = '1'
    pos = '10'
    ref = 'A'
    alt = 'G'

    simple_id = parse_simple_id(chrom, pos, ref, alt)
    assert simple_id == '_'.join([chrom, pos, ref, alt])

def test_parse_variant_id():
    chrom = '1'
    pos = '10'
    ref = 'A'
    alt = 'G'
    variant_type = 'clinical'

    variant_id = parse_variant_id(chrom, pos, ref, alt, variant_type)
    assert variant_id == generate_md5_key([chrom, pos, ref, alt, variant_type])

def test_parse_display_name():
    chrom = '1'
    pos = '10'
    ref = 'A'
    alt = 'G'
    variant_type = 'clinical'

    variant_id = parse_display_name(chrom, pos, ref, alt, variant_type)
    assert variant_id == '_'.join([chrom, pos, ref, alt, variant_type])

def test_parse_document_id():
    chrom = '1'
    pos = '10'
    ref = 'A'
    alt = 'G'
    case_id = 'cust000_1'
    variant_type = 'clinical'

    variant_id = parse_document_id(chrom, pos, ref, alt, variant_type, case_id)
    assert variant_id == generate_md5_key([chrom, pos, ref, alt, variant_type] + case_id.split('_'))

def test_parse_ids():
    variant = {
        'CHROM': '1',
        'POS': '10',
        'REF': 'A',
        'ALT': 'G',
    }
    case =  {'case_id': 'cust000_1','display_name': '1'}
    variant_type = 'clinical'

    variant_ids = parse_ids(variant, case, variant_type)

    assert variant_ids['simple_id'] == '_'.join(['1', '10', 'A', 'G'])
