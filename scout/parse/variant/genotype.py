# encoding: utf-8

def parse_genotypes(variant, case):
    """Parse the genotype calls for a variant
    
        Args:
            variant(dict)
            case(dict)
        Returns:
            genotypes(list(dict)): A list of genotypes
    """
    genotypes = []
    individuals = case['individuals']
    if individuals:
        for ind in individuals:
            genotypes.append(parse_genotype(variant, ind))

    return genotypes

def parse_genotype(variant, ind):
    """Get the genotype information in the proper format

         Args:
             variant (dict): A dictionary with the information about a variant
             ind_id (dict): A dictionary with individual information

         Returns:
             gt_call(dict)

    """
    # Initiate a mongo engine gt call object
    gt_call = {}
    ind_id = ind['individual_id']
    
    gt_call['individual_id'] = ind_id
    gt_call['display_name'] = ind['display_name']
    gt_call['genotype_call'] = None
    gt_call['read_depth'] = None
    gt_call['ref_depth'] = -1
    gt_call['alt_depth'] = -1
    gt_call['genotype_quality'] = None
    
    genotypes = variant.get('genotypes', {})
    # Fill the onbject with the relevant information:
    if ind_id in genotypes:
        gt_call['genotype_call'] = genotypes[ind_id].genotype
        
        gt_call['read_depth'] = genotypes[ind_id].depth_of_coverage
        
        try:
            gt_call['ref_depth'] = int(genotypes[ind_id].ref_depth)
        except (ValueError, TypeError):
            gt_call['ref_depth'] = -1
        
        try:
            gt_call['alt_depth'] = int(genotypes[ind_id].alt_depth)
        except (ValueError, TypeError):
            gt_call['alt_depth'] = -1
        
        gt_call['genotype_quality'] = genotypes[ind_id].genotype_quality

    return gt_call
