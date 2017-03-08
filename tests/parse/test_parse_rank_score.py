from scout.parse.variant.rank_score import parse_rank_score

def test_parse_rank_score(one_variant, parsed_case):
    """docstring for test_parse_rank_score"""
    rank_scores_dict = one_variant['rank_scores']
    
    rank_score = rank_scores_dict[parsed_case['display_name']]
    
    assert float(rank_score) == parse_rank_score(one_variant, parsed_case['display_name'])

def test_parse_rank_scores(variants, parsed_case):
    """docstring for test_parse_rank_score"""
    case_id = parsed_case['display_name']
    for variant in variants:
        rank_scores_dict = variant['rank_scores']
        
        rank_score = rank_scores_dict[case_id]
    
        assert float(rank_score) == parse_rank_score(variant, case_id)