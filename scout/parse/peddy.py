from scout.utils.convert import (make_bool, convert_number)

def parse_peddy_ped(lines):
    """Parse a peddy.ped file
    
    Args:
        lines(iterable(str))
    
    Returns:
        peddy_ped(list(dict))
    """
    peddy_ped = []
    header = []
    for i,line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            # Header line
            header = line.lstrip('#').split('\t')
        else:
            ind_info = dict(zip(header, line.split('\t')))
            
            # one of AFR AMR EAS EUR SAS UNKNOWN
            
            peddy_ped.append(ind_info)
    return peddy_ped
        
def parse_peddy_ped_check(lines):
    """Parse a .ped_check.csv file
    
    Args:
        lines(iterable(str))
    
    Returns:
        ped_check(list(dict))
    """
    ped_check = []
    header = []
    for i,line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            # Header line
            header = line.lstrip('#').split(',')
        else:
            pair_info = dict(zip(header, line.split(',')))
            
            # the number of sites at which sample_a was heterozygous
            pair_info['hets_a'] = convert_number(pair_info['hets_a'])
            
            # the number of sites at which sample_b was heterozygous
            pair_info['hets_b'] = convert_number(pair_info['hets_b'])
            
            # the number of sites at which the 2 samples shared no alleles 
            # (should approach 0 for parent-child pairs).
            pair_info['ibs0'] = convert_number(pair_info['ibs0'])
            
            # the number of sites and which the 2 samples where both 
            # hom-ref, both het, or both hom-alt.
            pair_info['ibs2'] = convert_number(pair_info['ibs2'])

            # the number of sites that was used to predict the relatedness.
            pair_info['n'] = convert_number(pair_info['n'])
            
            # the relatedness reported in the ped file.
            pair_info['rel'] = convert_number(pair_info['rel'])

            # the relatedness reported in the ped file.
            pair_info['pedigree_relatedness'] = convert_number(pair_info['pedigree_relatedness'])
            
            # difference between the preceding 2 colummns.
            pair_info['rel_difference'] = convert_number(pair_info['rel_difference'])

            # the number of sites at which both samples were hets.
            pair_info['shared_hets'] = convert_number(pair_info['shared_hets'])

            # boolean indicating that this pair is a parent-child pair 
            # according to the ped file.
            pair_info['pedigree_parents'] = make_bool(pair_info.get('pedigree_parents'))
            
            # boolean indicating that this pair is expected to be a parent-child
            # pair according to the ibs0 (< 0.012) calculated from the genotypes.
            pair_info['predicted_parents'] = make_bool(pair_info.get('predicted_parents'))
            
            # boolean indicating that the preceding 2 columns don’t match
            pair_info['parent_error'] = make_bool(pair_info.get('parent_error'))

            #  boolean indicating that rel > 0.75 and ibs0 < 0.012
            pair_info['sample_duplication_error'] = make_bool(pair_info.get('sample_duplication_error'))
            
            
            ped_check.append(pair_info)

    return ped_check

def parse_peddy_sex_check(lines):
    """Parse a .ped_check.csv file
    
    Args:
        lines(iterable(str))
    
    Returns:
        sex_check(list(dict))
    """
    sex_check = []
    header = []
    for i,line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            # Header line
            header = line.lstrip('#').split(',')
        else:
            ind_info = dict(zip(header, line.split(',')))
            error = ind_info.get('error')
            if error:
                if error in ['False', 'false']:
                    ind_info['error'] = False
                else:
                    ind_info['error'] = True
            try:
                ind_info['het_count'] = int(ind_info['het_count'])
            except ValueError:
                ind_info['het_count'] = None

            try:
                ind_info['het_ratio'] = float(ind_info['het_ratio'])
            except ValueError:
                ind_info['het_ratio'] = None

            try:
                ind_info['hom_alt_count'] = int(ind_info['hom_alt_count'])
            except ValueError:
                ind_info['hom_alt_count'] = None

            try:
                ind_info['hom_ref_count'] = int(ind_info['hom_ref_count'])
            except ValueError:
                ind_info['hom_ref_count'] = None
                
            sex_check.append(ind_info)

    return sex_check

