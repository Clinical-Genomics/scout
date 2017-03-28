from scout.parse.variant.frequency import parse_frequency, parse_frequencies

def test_parse_frequency():
    # GIVEN a variant dict with a frequency in info_dict
    variant = {
        'info_dict': {
            '1000G': ['0.01']
        }
    }
    
    # WHEN frequency is parsed
    frequency = parse_frequency(variant, '1000G')
    
    # THEN the frequency should be a float with correct value
    
    assert frequency == float(variant['info_dict']['1000G'][0])


def test_parse_frequency_non_existing_keyword():
    
    # GIVEN a variant dict with a frequency in info_dict    
    variant = {
        'info_dict': {
            '1000G': ['0.01']
        }
    }
    # WHEN frequency is parsed with wrong keyword
    frequency = parse_frequency(variant, 'EXACAF')
    
    # THEN the frequency should be None
    assert frequency == None

def test_parse_frequency_non_existing_freq():
    # GIVEN a variant dict with a frequency in info_dict without value
    variant = {
        'info_dict': {
            '1000G': []
        }
    }
    # WHEN frequency is parsed
    frequency = parse_frequency(variant, '1000G')

    # THEN the frequency should be None
    assert frequency == None

def test_parse_frequencies():
    # GIVEN a variant dict with a differenct frequencies
    variant = {
        'info_dict': {
            '1000GAF': ['0.01'],
            'EXACAF': ['0.001']
        }
    }
    # WHEN frequencies are parsed    
    frequencies = parse_frequencies(variant)
    
    # THEN the frequencies should be returned in a dictionary
    assert frequencies['thousand_g'] == float(variant['info_dict']['1000GAF'][0])
    assert frequencies['exac'] == float(variant['info_dict']['EXACAF'][0])
