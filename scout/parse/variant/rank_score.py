
def parse_rank_score(variant, case_id):
    """Parse the rank score
    
        Args:
            variant(cyvcf2.Variant): A cyvcf2 variant
            case_id(str)
        
        Returns:
            rank_score(float)
    """
    rank_score = None
    rank_score_entry = variant.INFO.get('RankScore')
    
    if rank_score_entry:
        for family_info in rank_score_entry.split(','):
            splitted_info = family_info.split(':')
            if case_id == splitted_info[0]:
                rank_score = float(splitted_info[1])
    
    return rank_score
    