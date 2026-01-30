import logging
from typing import Any

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


def cyvcf2_get_field(obj: Variant, path: str) -> Any:
    """Walk the provided path in a cyvcf2 variant and collect a potential value."""
    if not path:
        return None

    for p in path.split("."):
        if obj is None:
            return None
        obj = obj.get(p) if hasattr(obj, "get") else getattr(obj, p, None)
    return obj


def parse_rank_score_other(parsed_variant: dict, variant: dict):
    """Parse variant and save any additional rank scores.
    These scores are defined under scout.models.variant.variant.RANK_SCORE_OTHER
    """
    for category, scores in RANK_SCORE_OTHER.items():
        if parsed_variant["category"] != category:
            continue

        for score, features in scores.items():
            raw_score = cyvcf2_get_field(variant, features.get("score_key"))
            if not raw_score:
                continue

            parsed_variant.setdefault("rank_score_other", {})
            parsed_variant["rank_score_other"].setdefault(score, {})

            parsed_variant["rank_score_other"][score]["value"] = features["score_type"](raw_score)
