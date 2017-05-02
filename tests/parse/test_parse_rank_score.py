from scout.parse.variant.rank_score import parse_rank_score

def test_parse_rank_score(cyvcf2_variant):
    rank_scores_info = cyvcf2_variant.INFO['RankScore']
    variant_score = rank_scores_info.split(':')[1]
    family_id = rank_scores_info.split(':')[0]
    
    rank_score = parse_rank_score(cyvcf2_variant, family_id)
    
    assert float(variant_score) == rank_score

# def test_parse_rank_scores(variants, parsed_case):
#     """docstring for test_parse_rank_score"""
#     case_id = parsed_case['display_name']
#     for variant in variants:
#         rank_scores_dict = variant['rank_scores']
#
#         rank_score = rank_scores_dict[case_id]
#
#         assert float(rank_score) == parse_rank_score(variant, case_id)