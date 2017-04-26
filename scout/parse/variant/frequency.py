


def parse_frequencies(variant):
    """Add the frequencies to a variant
    
    This needs to be expanded so that other keys are allowed and easy
    to implement.

    Args:
        variant(dict): A parsed vcf variant

    Returns:
        frequencies(dict): A dictionary with the relevant frequencies
    """
    frequencies = {}
    # These lists could be extended...
    thousand_genomes_keys = ['1000GAF']
    thousand_genomes_max_keys = ['1000G_MAX_AF']
    exac_keys = ['EXACAF']
    exac_max_keys = ['ExAC_MAX_AF', 'EXAC_MAX_AF']
    
    for test_key in thousand_genomes_keys:
        thousand_g = parse_frequency(variant, test_key)
        if thousand_g:
            frequencies['thousand_g'] = thousand_g
            break

    for test_key in thousand_genomes_max_keys:
        thousand_g_max = parse_frequency(variant, test_key)
        if thousand_g_max:
            frequencies['thousand_g_max'] = thousand_g_max
            break

    for test_key in exac_keys:
        exac = parse_frequency(variant, test_key)
        if exac:
            frequencies['exac'] = exac
            break

    for test_key in exac_max_keys:
        exac_max = parse_frequency(variant, test_key)
        if exac_max:
            frequencies['exac_max'] = exac_max
            break
    
    #These are SV-specific frequencies
    thousand_g_left = parse_frequency(variant, 'left_1000GAF')
    if thousand_g_left:
        frequencies['thousand_g_left'] = thousand_g_left 
    
    thousand_g_right = parse_frequency(variant, 'right_1000GAF')
    if thousand_g_right:
        frequencies['thousand_g_right'] = thousand_g_right 

    return frequencies


def parse_frequency(variant, info_key):
    """Parse any frequency from the info dict
    
    Args:
        variant(dict)
        info_key(str)
    
    Returns:
        frequency(float): or None if frequency does not exist
    """
    raw_annotation = variant['info_dict'].get(info_key)
    raw_annotation = None if raw_annotation == '.' else raw_annotation
    frequency = float(raw_annotation[0]) if raw_annotation else None
    return frequency
