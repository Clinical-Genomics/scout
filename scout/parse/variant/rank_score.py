
def parse_rank_score(variant, case_id):
    """Parse the rank score
    
        Args:
            variant(dict): A variant dictionary
            case_id(str)
        
        Returns:
            rank_score(float)
    """
    rank_score = float(variant.get('rank_scores', {}).get(case_id, 0.0))
    
    return rank_score
    