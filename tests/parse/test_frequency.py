from scout.parse.frequency import parse_frequency, parse_frequencies

def test_parse_frequency():
    variant = {
        'info_dict': {
            '1000G': ['0.01']
        }
    }
    
    assert parse_frequency(variant, '1000G') == float(variant['info_dict']['1000G'][0])


def test_parse_frequency_non_existing_keyword():
    variant = {
        'info_dict': {
            '1000G': ['0.01']
        }
    }
    
    assert parse_frequency(variant, 'EXACAF') == None

def test_parse_frequency_non_existing_freq():
    variant = {
        'info_dict': {
            '1000G': []
        }
    }
    
    assert parse_frequency(variant, '1000G') == None

def test_parse_frequencies():
    variant = {
        'info_dict': {
            '1000GAF': ['0.01'],
            'EXACAF': ['0.001']
        }
    }
    
    frequencies = parse_frequencies(variant)
    
    assert frequencies['thousand_g'] == float(variant['info_dict']['1000GAF'][0])
    assert frequencies['exac'] == float(variant['info_dict']['EXACAF'][0])
