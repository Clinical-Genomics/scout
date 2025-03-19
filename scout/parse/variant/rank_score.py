def parse_rank_score(rank_score_entry: str, case_id: str) -> float:
    """Parse the rank score from the raw rank score entry"""
    rank_score = None
    if rank_score_entry:
        for family_info in rank_score_entry.split(","):
            split_info = family_info.split(":")
            if case_id == split_info[0]:
                rank_score = float(split_info[1])
    return rank_score
