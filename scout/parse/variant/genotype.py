# encoding: utf-8

def parse_genotypes(variant, case, individual_positions):
    """Parse the genotype calls for a variant
    
        Args:
            variant(dict)
            case(dict)
            individual_positions(dict)
        Returns:
            genotypes(list(dict)): A list of genotypes
    """
    genotypes = []
    individuals = case['individuals']
    if individuals:
        for ind in individuals:
            pos = individual_positions[ind['individual_id']]
            genotypes.append(parse_genotype(variant, ind, pos))

    return genotypes

def parse_genotype(variant, ind, pos):
    """Get the genotype information in the proper format

    Args:
        variant(dict): A dictionary with the information about a variant
        ind_id(dict): A dictionary with individual information
        pos(int): What position the ind has in vcf

    Returns:
        gt_call(dict)

    """
    gt_call = {}
    ind_id = ind['individual_id']
    
    gt_call['individual_id'] = ind_id
    gt_call['display_name'] = ind['display_name']
    
    # Fill the object with the relevant information:
    genotype = variant.genotypes[pos]
    gt_call['genotype_call'] = '/'.join([str(genotype[0]), str(genotype[1])])

    read_depth = int(variant.gt_depths[pos])
    if read_depth == -1:
        # If read depth could not be parsed by cyvcf2, try to get it manually
        if 'DP' in variant.FORMAT:
            read_depth = int(variant.format('DP')[pos][0])
    gt_call['read_depth'] = read_depth
    
    alt_depth = int(variant.gt_alt_depths[pos])
    if alt_depth == -1:
        if 'VD' in variant.FORMAT:
            alt_depth = int(variant.format('VD')[pos][0])
    gt_call['alt_depth'] = alt_depth
    
    ref_depth = int(variant.gt_ref_depths[pos])
    if ref_depth == -1:
        if (read_depth != -1 and alt_depth != -1):
            ref_depth = read_depth - alt_depth
    gt_call['ref_depth'] = ref_depth
    
    alt_frequency = float(variant.gt_alt_depths[pos])
    if alt_frequency == -1:
        if 'AF' in variant.FORMAT:
            alt_frequency = float(variant.format('AF')[pos][0])
    
    gt_call['alt_frequency'] = alt_frequency

    gt_call['genotype_quality'] = int(variant.gt_quals[pos])

    return gt_call
