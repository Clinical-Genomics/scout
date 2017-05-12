from scout.parse.variant.rank_score import parse_rank_score

def test_parse_rank_score():
    rank_scores_info = "123:10"
    variant_score = 10.0
    family_id = '123'
    
    parsed_rank_score = parse_rank_score(rank_scores_info, family_id)
    
    assert variant_score == parsed_rank_score

def test_parse_rank_score_no_score():
    rank_scores_info = ""
    family_id = '123'
    
    parsed_rank_score = parse_rank_score(rank_scores_info, family_id)
    
    assert parsed_rank_score == None


# def test_parse_rank_scores(variants, parsed_case):
#     """docstring for test_parse_rank_score"""
#     case_id = parsed_case['display_name']
#     for variant in variants:
#         rank_scores_dict = variant['rank_scores']
#
#         rank_score = rank_scores_dict[case_id]
#
#         assert float(rank_score) == parse_rank_score(variant, case_id)