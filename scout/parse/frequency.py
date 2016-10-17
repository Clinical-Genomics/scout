
def parse_frequencies(variant):
    """Add the frequencies to a variant
    
        Args:
            variant(dict): A parsed vcf variant
    
        Returns:
            frequencies(dict): A dictionary with the relevant frequencies
    """
    frequencies = {}
    frequencies['thousand_g'] = parse_frequency(variant, '1000GAF')
    frequencies['thousand_g_max'] = parse_frequency(variant, '1000G_MAX_AF')
    frequencies['exac'] = parse_frequency(variant, 'EXACAF')
    frequencies['exac_max'] = parse_frequency(variant, 'ExAC_MAX_AF')
    
    return frequencies


def parse_frequency(variant, info_key):
    """Parse the thousand genomes frequency"""
    raw_annotation = variant['info_dict'].get(info_key)
    frequency = None
    if raw_annotation:
        frequency = float(raw_annotation[0])
    return frequency

    
    