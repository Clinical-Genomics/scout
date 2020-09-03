def parse_rank_score(rank_score_entry, case_id):
    """Parse the rank score

    Args:
        rank_score_entry(str): The raw rank score entry
        case_id(str)

    Returns:
        rank_score(float)
    """
    rank_score = None
    if rank_score_entry:
        for family_info in rank_score_entry.split(","):
            splitted_info = family_info.split(":")
            if case_id == splitted_info[0]:
                rank_score = float(splitted_info[1])
    return rank_score
