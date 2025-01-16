# coding=UTF-8
from typing import Optional

from scout.constants.ccv import CCV_COMPLETE_MAP, CCV_POTENTIAL_CONFLICTS


def get_ccv_points(ccv_terms: set) -> int:
    """
    Use the algorithm described in Clingen-CGC-VIGG classification paper (Horak 2022)
    Given a set of CCV evidence criteria terms
    for each term,
      check prefixes if no suffix match or stand-alone criteria match

    O positive, SB negative.
    VS 8 points, S 4, M 2, P 1.

    If no terms return None

    Args:
        ccv_terms(set(str)): A collection of prediction terms
    Returns:
        points(int):"""

    ovs_terms = []
    os_terms = []
    om_terms = []
    op_terms = []
    sbvs_terms = []
    sbs_terms = []
    sbm_terms = []
    sbp_terms = []

    prefix_map = {
        "OVS": ovs_terms,
        "OS": os_terms,
        "OM": om_terms,
        "OP": op_terms,
        "SBVS": sbvs_terms,
        "SBS": sbs_terms,
        "SBM": sbm_terms,
        "SBP": sbp_terms,
    }

    suffix_map = {
        "_Strong": {"O": os_terms, "SB": sbs_terms},
        "_Moderate": {"O": om_terms, "SB": sbm_terms},
        "_Supporting": {"O": op_terms, "SB": sbp_terms},
    }

    for term in ccv_terms:
        for suffix, prefix_dict in suffix_map.items():
            if term.endswith(suffix):
                for prefix, term_list in prefix_dict.items():
                    if term.startswith(prefix):
                        term_list.append(term)
                        break
                else:
                    continue
                break
        else:
            for prefix, term_list in prefix_map.items():
                if term.startswith(prefix):
                    term_list.append(term)
                    break
    points = (
        8 * len(ovs_terms)
        + 4 * len(os_terms)
        + 2 * len(om_terms)
        + len(op_terms)
        - 8 * len(sbvs_terms)
        - 4 * len(sbs_terms)
        - 2 * len(sbm_terms)
        - len(sbp_terms)
    )
    return points


def get_ccv(ccv_terms: set) -> Optional[str]:
    """Use the algorithm described in Clingen-CGC-VIGG classification paper (Horak 2022)

    If no terms return None

    O >= 10
    OP 6 <= p <= 9
    VUS 0 <= p <= 5
    LB -1 <= p <= -6
    B <= -7

    Args:
        ccv_terms(set(str)): A collection of prediction terms

    Returns:
        prediction(str): in ['uncertain_significance','benign','likely_benign',
                             'likely_oncogenic','oncogenic']

    """
    if not ccv_terms:
        return None

    points = get_ccv_points(ccv_terms)

    if points <= -7:
        prediction = "benign"
    elif points <= -1:
        prediction = "likely_benign"
    elif points <= 5:
        prediction = "uncertain_significance"
    elif points <= 9:
        prediction = "likely_oncogenic"
    elif points >= 10:
        prediction = "oncogenic"

    return prediction


def get_ccv_temperature(ccv_terms: set) -> Optional[dict]:
    """
    Use the algorithm described in Clingen-CGC-VIGG classification paper (Horak 2022)

    O >= 10
    OP 6 <= p <= 9
    VUS 0 <= p <= 5
    LB -1 <= p <= -6
    B <= -7

    If no terms return None

    Args:
        ccv_terms(set(str)): A collection of prediction terms

    Returns:
        dict:
            temperature:
        (points, temperature, point_classification)

    """
    TEMPERATURE_STRINGS = {
        -1: {"label": "B/LB", "color": "success", "icon": "fa-times"},
        0: {"label": "Ice cold", "color": "info", "icon": "fa-icicles"},
        1: {"label": "Cold", "color": "info", "icon": "fa-snowman"},
        2: {"label": "Cold", "color": "info", "icon": "fa-snowflake"},
        3: {"label": "Tepid", "color": "yellow", "icon": "fa-temperature-half"},
        4: {"label": "Warm", "color": "orange", "icon": "fa-mug-hot"},
        5: {"label": "Hot", "color": "red", "icon": "fa-pepper-hot"},
        6: {"label": "LO/O", "color": "danger", "icon": "fa-stethoscope"},
    }

    if not ccv_terms:
        return {}

    points = get_ccv_points(ccv_terms)

    if points <= -7:
        point_classification = "benign"
        temperature_icon = TEMPERATURE_STRINGS[-1].get("icon")
    elif points <= -1:
        point_classification = "likely_benign"
        temperature_icon = TEMPERATURE_STRINGS[-1].get("icon")
    elif points <= 5:
        point_classification = "uncertain_significance"
    elif points <= 9:
        point_classification = "likely_oncogenic"
        temperature_icon = TEMPERATURE_STRINGS[6].get("icon")
    elif points >= 10:
        point_classification = "oncogenic"
        temperature_icon = TEMPERATURE_STRINGS[6].get("icon")

    temperature_class = CCV_COMPLETE_MAP[point_classification].get("color")
    temperature = CCV_COMPLETE_MAP[point_classification].get("label")

    if point_classification == "uncertain_significance":
        temperature_class = TEMPERATURE_STRINGS[points].get("color")
        temperature = TEMPERATURE_STRINGS[points].get("label")
        temperature_icon = TEMPERATURE_STRINGS[points].get("icon")

    return {
        "points": points,
        "temperature": temperature,
        "temperature_class": temperature_class,
        "temperature_icon": temperature_icon,
        "point_classification": CCV_COMPLETE_MAP[point_classification].get("short"),
    }


def get_ccv_conflicts(ccv_terms: set) -> list:
    """Check potential conflict paris, return list of reference strings."""

    conflicts = []
    for t1, t2, reference in CCV_POTENTIAL_CONFLICTS:
        if t1 in ccv_terms and t2 in ccv_terms:
            conflicts.append(reference)

    return conflicts
