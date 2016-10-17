from scout.models import GTCall

def build_genotype(gt_call):
    """Build a mongoengine GTCall
    
        Args:
            gt_call(dict)
        
        Returns:
            gt_obj(GTCall): A mongoengine genotype call
    """
    gt_obj = GTCall(
        sample_id = gt_call['individual_id'],
        display_name = gt_call['display_name'],
        genotype_call = gt_call['genotype_call'],
        allele_depths = [gt_call['ref_depth'], gt_call['alt_depth']],
        read_depth = gt_call['read_depth'],
        genotype_quality = gt_call['genotype_quality']
    )
    
    return gt_obj