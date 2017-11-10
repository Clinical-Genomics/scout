from scout.parse.variant.frequency import (parse_frequency, parse_frequencies, 
                                           parse_sv_frequencies)

def test_parse_frequency(cyvcf2_variant):
    # GIVEN a variant dict with a frequency in info_dict
    variant = cyvcf2_variant
    
    variant.INFO['1000G'] = 0.01
    
    # WHEN frequency is parsed
    frequency = parse_frequency(variant, '1000G')
    
    # THEN the frequency should be a float with correct value
    
    assert frequency == float(variant.INFO['1000G'])


def test_parse_frequency_non_existing_keyword(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a frequency in info_dict    
    variant.INFO['1000G'] = 0.01
    
    # WHEN frequency is parsed with wrong keyword
    frequency = parse_frequency(variant, 'EXACAF')
    
    # THEN the frequency should be None
    assert frequency == None

def test_parse_frequency_non_existing_freq(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a frequency in info_dict without value
    variant.INFO['1000G'] = None
    
    # WHEN frequency is parsed
    frequency = parse_frequency(variant, '1000G')

    # THEN the frequency should be None
    assert frequency == None

def test_parse_frequencies(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO['1000GAF'] = '0.01'
    variant.INFO['EXACAF'] = '0.001'
    
    # WHEN frequencies are parsed    
    frequencies = parse_frequencies(variant, [])
    
    # THEN the frequencies should be returned in a dictionary
    assert frequencies['thousand_g'] == float(variant.INFO['1000GAF'])
    assert frequencies['exac'] == float(variant.INFO['EXACAF'])

def test_parse_sv_frequencies_clingen_benign(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN a variant dict with a differenct frequencies
    variant.INFO['clingen_cgh_benignAF'] = '0.01'
    variant.INFO['clingen_cgh_benign'] = '3'
    
    # WHEN frequencies are parsed    
    frequencies = parse_sv_frequencies(variant)
    
    # THEN the frequencies should be returned in a dictionary
    assert frequencies['clingen_cgh_benignAF'] == float(variant.INFO['clingen_cgh_benignAF'])
    assert frequencies['clingen_cgh_benign'] == int(variant.INFO['clingen_cgh_benign'])
