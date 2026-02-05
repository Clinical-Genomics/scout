import logging

from cyvcf2.cyvcf2 import Variant

from scout.models.variant.variant import RANK_SCORE_OTHER

LOG = logging.getLogger(__name__)


def parse_rank_score(rank_score_entry: str, case_id: str) -> float:
    """Parse the rank score from the raw rank score entry"""
    rank_score = None
    if rank_score_entry:
        for family_info in rank_score_entry.split(","):
            split_info = family_info.split(":")
            if case_id == split_info[0]:
                rank_score = float(split_info[1])
    return rank_score


def parse_rank_score_other(parsed_variant: dict, variant: Variant):
    """Parse variant and save additional rank scores from RANK_SCORE_OTHER."""

    category_scores = RANK_SCORE_OTHER.get(parsed_variant["category"])
    if not category_scores:
        return

    rank_scores = parsed_variant.setdefault("rank_score_other", {})

    for score_name, features in category_scores.items():
        raw_score = variant.INFO.get(features.get("score_key"))
        if raw_score is None:
            continue

        score_entry = rank_scores.setdefault(score_name, {})
        score_entry["value"] = features["score_type"](raw_score)

        score_desc_key = features.get("score_desc")
        if score_desc_key and variant.INFO.get(score_desc_key):
            raw_desc = variant.INFO[score_desc_key].strip("[]").rstrip(",")
            if raw_desc:
                score_entry["desc"] = {
                    k: float(v) for k, v in (item.split("=") for item in raw_desc.split(","))
                }
