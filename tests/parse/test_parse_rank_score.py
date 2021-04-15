from scout.parse.variant.rank_score import parse_rank_score
from scout.parse.variant.variant import parse_variant


def test_parse_rank_score():
    ## GIVEN a rank score string on genmod format
    rank_scores_info = "123:10"
    variant_score = 10.0
    family_id = "123"
    ## WHEN parsing the rank score
    parsed_rank_score = parse_rank_score(rank_scores_info, family_id)
    ## THEN assert that the correct rank score is parsed
    assert variant_score == parsed_rank_score


def test_parse_rank_score_no_score():
    ## GIVEN a empty rank score string
    rank_scores_info = ""
    family_id = "123"
    ## WHEN parsing the rank score
    parsed_rank_score = parse_rank_score(rank_scores_info, family_id)
    ## THEN assert that None is returned
    assert parsed_rank_score == None


def test_parse_rank_score_variant(cyvcf2_variant, case_obj, scout_config):
    ## GIVEN a variant
    rank_score = 15
    case_id = case_obj["_id"]
    ## WHEN adding a rank score string to the INFO field
    rank_score_str = f"{case_id}:{rank_score}"
    cyvcf2_variant.INFO["RankScore"] = rank_score_str

    ## WHEN parsing the variant
    var_info = parse_variant(cyvcf2_variant, case_obj)
    ## THEN assert that the correct score is parsed
    assert var_info["rank_score"] == rank_score
