# encoding: utf-8

GENOTYPE_MAP = {0: '0', 1: '1', -1:'.'}

def parse_genotypes(variant, case, individual_positions):
    """Parse the genotype calls for a variant
    
        Args:
            variant(cyvcf2.Variant)
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
    
    Sv specific format fields:
    
    ##FORMAT=<ID=PE,Number=1,Type=Integer,
    Description="Number of paired-ends that support the event">
    
    ##FORMAT=<ID=PR,Number=.,Type=Integer,
    Description="Spanning paired-read support for the ref and alt alleles 
                in the order listed">
    
    ##FORMAT=<ID=RC,Number=1,Type=Integer,
    Description="Raw high-quality read counts for the SV">
    
    ##FORMAT=<ID=RCL,Number=1,Type=Integer,
    Description="Raw high-quality read counts for the left control region">
    
    ##FORMAT=<ID=RCR,Number=1,Type=Integer,
    Description="Raw high-quality read counts for the right control region">
    
    ##FORMAT=<ID=RR,Number=1,Type=Integer,
    Description="# high-quality reference junction reads">
    
    ##FORMAT=<ID=RV,Number=1,Type=Integer,
    Description="# high-quality variant junction reads">
    
    ##FORMAT=<ID=SR,Number=1,Type=Integer,
    Description="Number of split reads that support the event">
    
    Args:
        variant(cyvcf2.Variant)
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
    ref_call = genotype[0]
    alt_call = genotype[1]
    gt_call['genotype_call'] = '/'.join([GENOTYPE_MAP[ref_call], 
                                         GENOTYPE_MAP[alt_call]])
    
    paired_end_alt = None
    paired_end_ref = None
    split_read_alt = None
    split_read_ref = None

    print((variant.CHROM, variant.POS))
    # Check if PE is annotated
    # This is the number of paired end reads that supports the variant
    if 'PE' in variant.FORMAT:
        try:
            print('PE')
            print(variant.format('PE'))
            value = int(variant.format('PE')[pos])
            print(value)
            if not value < 0:
                paired_end_alt = value
        except ValueError as e:
            pass
    
    # Check if PR is annotated
    # Number of paired end reads that supports ref and alt
    if 'PR' in variant.FORMAT:
        print('PR')
        print(variant.format('PR'))
        values = variant.format('PR')[pos]
        print(values)
        try:
            alt_value = int(values[1])
            ref_value = int(values[0])
            if not alt_value < 0:
                paired_end_alt = alt_value
            if not ref_value < 0:
                paired_end_ref = ref_value
        except ValueError as r:
            pass
    
    # Check if 'SR' is annotated
    # This field is used different by different callers
    if 'SR' in variant.FORMAT:
        print('SR')
        print(variant.format('SR'))
        values = variant.format('SR')[pos]
        print(values)
        alt_value = 0
        ref_value = 0
        if len(values) == 1:
            alt_value = int(values[0])
        elif len(values) == 2:
            alt_value = int(values[1])
            ref_value = int(values[0])
        if not alt_value < 0:
            split_read_alt = alt_value
        if not ref_value < 0:
            split_read_ref = ref_value
            

    alt_depth = int(variant.gt_alt_depths[pos])
    if alt_depth == -1:
        if 'VD' in variant.FORMAT:
            alt_depth = int(variant.format('VD')[pos][0])
        
        if (paired_end_alt != None or split_read_alt != None):
            alt_depth = 0
            if paired_end_alt:
                alt_depth += paired_end_alt
            if split_read_alt:
                alt_depth += split_read_alt
             
    gt_call['alt_depth'] = alt_depth
    
    ref_depth = int(variant.gt_ref_depths[pos])
    if ref_depth == -1:
        if (paired_end_ref != None or split_read_ref != None):
            ref_depth = 0
            if paired_end_ref:
                ref_depth += paired_end_ref
            if split_read_ref:
                ref_depth += split_read_ref

    gt_call['ref_depth'] = ref_depth
    
    alt_frequency = float(variant.gt_alt_depths[pos])
    if alt_frequency == -1:
        if 'AF' in variant.FORMAT:
            alt_frequency = float(variant.format('AF')[pos][0])

    read_depth = int(variant.gt_depths[pos])
    if read_depth == -1:
        # If read depth could not be parsed by cyvcf2, try to get it manually
        if 'DP' in variant.FORMAT:
            read_depth = int(variant.format('DP')[pos][0])
        elif (alt_depth != -1 and ref_depth != -1):
            read_depth = alt_depth + ref_depth

    if (ref_depth==0 and read_depth!=-1 and alt_depth!=-1):
        ref_depth = read_depth - alt_depth


    gt_call['read_depth'] = read_depth

    gt_call['alt_frequency'] = alt_frequency

    gt_call['genotype_quality'] = int(variant.gt_quals[pos])

    return gt_call
