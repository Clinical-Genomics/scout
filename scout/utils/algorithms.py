import logging

LOG = logging.getLogger(__name__)


def ui_score(set_1, set_2):
    """Get the ui score of two sets

    Given two bags of HPO terms, p and q, the UI score is defined as:

        - let I(t) for a set of terms t, be the set of terms in t and all the ancestors of the terms
          in t
        - UI(p, q) = Size{Intersection{I(p), I(q)}} / Size{Union{I(p), I(q)}}

    The higher UI score, the more similar they are

    Args:
        set_1, set_2 (set(str))

    Returns:
        ui_score (float)
    """
    LOG.debug("Set 1: %s", ", ".join(set_1))
    LOG.debug("Set 2: %s", ", ".join(set_2))
    if not (set_1 and set_2):
        return 0
    ui_score = len(set_1.intersection(set_2)) / len(set_1.union(set_2))
    LOG.debug("Found ui score: %s", ui_score)

    return ui_score
