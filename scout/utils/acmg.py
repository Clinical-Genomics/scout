# coding=UTF-8


from typing import Optional

from scout.constants import ACMG_COMPLETE_MAP
from scout.constants.acmg import ACMG_POTENTIAL_CONFLICTS


def is_pathogenic(pvs, ps_terms, pm_terms, pp_terms):
    """Check if the criterias for Pathogenic is fullfilled

    The following are descriptions of Pathogenic clasification from ACMG paper:

    Pathogenic
      (i) 1 Very strong (PVS1) AND
        (a) ≥1 Strong (PS1–PS4) OR
        (b) ≥2 Moderate (PM1–PM6) OR
        (c) 1 Moderate (PM1–PM6) and 1 supporting (PP1–PP5) OR
        (d) ≥2 Supporting (PP1–PP5)
      (ii) ≥2 Strong (PS1–PS4) OR
      (iii) 1 Strong (PS1–PS4) AND
        (a)≥3 Moderate (PM1–PM6) OR
        (b)2 Moderate (PM1–PM6) AND ≥2 Supporting (PP1–PP5) OR
        (c)1 Moderate (PM1–PM6) AND ≥4 supporting (PP1–PP5)

    Args:
        pvs(bool): Pathogenic Very Strong
        ps_terms(list(str)): Pathogenic Strong terms
        pm_terms(list(str)): Pathogenic Moderate terms
        pp_terms(list(str)): Pathogenic Supporting terms

    Returns:
        bool: if classification indicates Pathogenic level
    """
    if pvs:
        # Pathogenic (i)(a):
        if ps_terms:
            return True
        if pm_terms:
            # Pathogenic (i)(c):
            if pp_terms:
                return True
            # Pathogenic (i)(b):
            if len(pm_terms) >= 2:
                return True
        # Pathogenic (i)(d):
        if len(pp_terms) >= 2:
            return True
    if ps_terms:
        # Pathogenic (ii):
        if len(ps_terms) >= 2:
            return True
        # Pathogenic (iii)(a):
        if pm_terms:
            if len(pm_terms) >= 3:
                return True
            elif len(pm_terms) >= 2:
                if len(pp_terms) >= 2:
                    return True
            elif len(pp_terms) >= 4:
                return True
    return False


def is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms):
    """Check if the criterias for Likely Pathogenic is fullfilled

    The following are descriptions of Likely Pathogenic clasification from ACMG paper:

    Likely pathogenic
      (i) 1 Very strong (PVS1) AND 1 moderate (PM1– PM6) OR
      (ii) 1 Strong (PS1–PS4) AND 1–2 moderate (PM1–PM6) OR
      (iii) 1 Strong (PS1–PS4) AND ≥2 supporting (PP1–PP5) OR
      (iv)  ≥3 Moderate (PM1–PM6) OR
      (v) 2 Moderate (PM1–PM6) AND ≥2 supporting (PP1–PP5) OR
      (vi) 1 Moderate (PM1–PM6) AND ≥4 supportin (PP1–PP5)

    Args:
        pvs(bool): Pathogenic Very Strong
        ps_terms(list(str)): Pathogenic Strong terms
        pm_terms(list(str)): Pathogenic Moderate terms
        pp_terms(list(str)): Pathogenic Supporting terms

    Returns:
        bool: if classification indicates Likely Pathogenic level
    """
    if pvs:
        # Likely Pathogenic (i):
        if pm_terms:
            return True

    if ps_terms:
        # Likely Pathogenic (ii):
        if pm_terms:
            return True
        # Likely Pathogenic (iii):
        if len(pp_terms) >= 2:
            return True

    if pm_terms:
        # Likely Pathogenic (iv):
        if len(pm_terms) >= 3:
            return True
        # Likely Pathogenic (v):
        elif len(pm_terms) >= 2:
            if len(pp_terms) >= 2:
                return True
        # Likely Pathogenic (vi):
        elif len(pp_terms) >= 4:
            return True

    return False


def is_benign(ba, bs_terms):
    """Check if criterias for Benign are fullfilled

    The following are descriptions of Benign clasification from ACMG paper:

    Benign
      (i) 1 Stand-alone (BA1) OR
      (ii) ≥2 Strong (BS1–BS4)

    Args:
        ba(bool): Stand Alone term for evidence of benign impact
        bs_terms(list(str)): Terms that indicate strong evidence for benign variant

    Returns:
        bool: if classification indicates Benign level
    """
    # Benign (i)
    if ba:
        return True
    # Benign (ii)
    if len(bs_terms) >= 2:
        return True
    return False


def is_likely_benign(bs_terms, bp_terms):
    """Check if criterias for Likely Benign are fullfilled

    The following are descriptions of Likely Benign clasification from ACMG paper:

    Likely Benign
      (i) 1 Strong (BS1–BS4) and 1 supporting (BP1– BP7) OR
      (ii) ≥2 Supporting (BP1–BP7)

    Args:
        bs_terms(list(str)): Terms that indicate strong evidence for benign variant
        bp_terms(list(str)): Terms that indicate supporting evidence for benign variant

    Returns:
        bool: if classification indicates Benign level
    """
    if bs_terms:
        # Likely Benign (i)
        if bp_terms:
            return True
    # Likely Benign (ii)
    if len(bp_terms) >= 2:
        return True

    return False


def get_acmg_criteria(acmg_terms: set) -> tuple:
    """
    Given a set of ACMG evidence criteria terms, that may be strength modified with suffixes.
    For each term,
        first, Strength modified criteria suffixes should count towards their modified score.
        then, we need to see if we match any of the two stand-alone terms. If so, set their respective booleans.
        finally, check remaining prefixes if no suffix match or stand-alone criteria match

    Return a tuple with
        pvs: This variable indicates if Pathogenicity Very Strong exists
        ps_terms: Collection of terms with Pathogenicity Strong
        pm_terms: Collection of terms with Pathogenicity moderate
        pp_terms: Collection of terms with Pathogenicity supporting
        ba: This variable indicates if Benign impact stand-alone exists
        bs_terms: Collection of terms with Benign evidence Strong
        bp_terms: Collection of terms with supporting Benign evidence
    """

    pvs = False
    ps_terms = []
    pm_terms = []
    pp_terms = []

    ba = False
    bs_terms = []
    bp_terms = []

    suffix_map = {
        "_Strong": {"P": ps_terms, "B": bs_terms},
        "_Moderate": {"P": pm_terms},
        "_Supporting": {"P": pp_terms, "B": bp_terms},
    }

    prefix_map = {
        "PS": ps_terms,
        "PM": pm_terms,
        "PP": pp_terms,
        "BS": bs_terms,
        "BP": bp_terms,
    }

    for term in acmg_terms:
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
            if term.startswith("PVS"):
                pvs = True
            elif term.startswith("BA"):
                ba = True
            else:
                for prefix, term_list in prefix_map.items():
                    if term.startswith(prefix):
                        term_list.append(term)
                        break

    return (pvs, ps_terms, pm_terms, pp_terms, ba, bs_terms, bp_terms)


def get_acmg(acmg_terms: set) -> Optional[str]:
    """Use the algorithm described in ACMG paper (Richards 2015) to get a ACMG classification

    Modifying strength of a term is possible by adding a string describing its new level: "PP1_Strong" or
    "PVS1_Moderate".

    BA is considered fully Stand Alone.

    If no terms return None

    Args:
        acmg_terms(set(str)): A collection of prediction terms

    Returns:
        prediction(str): in ['uncertain_significance','benign','likely_benign',
                             'likely_pathogenic','pathogenic']

    """
    if not acmg_terms:
        return None

    (pvs, ps_terms, pm_terms, pp_terms, ba, bs_terms, bp_terms) = get_acmg_criteria(acmg_terms)

    if ba:
        return "benign"

    prediction = "uncertain_significance"

    pathogenic = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    likely_pathogenic = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    benign = is_benign(ba, bs_terms)
    likely_benign = is_likely_benign(bs_terms, bp_terms)

    if pathogenic or likely_pathogenic:
        if benign or likely_benign:
            prediction = "uncertain_significance"
        elif pathogenic:
            prediction = "pathogenic"
        else:
            prediction = "likely_pathogenic"
    else:
        if benign:
            prediction = "benign"
        if likely_benign:
            prediction = "likely_benign"

    return prediction


def get_acmg_temperature(acmg_terms: set) -> Optional[dict]:
    """
    Use the algorithm described in Tavtigian 2020 to classifiy variants.

    PVS 8 points, S 4, M 2, P 1.
    This gives:

    P > 10
    LP 6 < p < 9
    VUS 0 < p < 5
    LB -1 < p < -6
    B < -7

    If no terms return None

    Args:
        acmg_terms(set(str)): A collection of prediction terms

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
        6: {"label": "LP/P", "color": "danger", "icon": "fa-stethoscope"},
    }

    if not acmg_terms:
        return {}

    (pvs, ps_terms, pm_terms, pp_terms, ba, bs_terms, bp_terms) = get_acmg_criteria(acmg_terms)

    if ba:
        points = -8
    else:
        points = (
            8 * pvs
            + 4 * len(ps_terms)
            + 2 * len(pm_terms)
            + len(pp_terms)
            - 4 * len(bs_terms)
            - len(bp_terms)
        )

    if points <= -7:
        point_classification = "benign"
        temperature_icon = TEMPERATURE_STRINGS[-1].get("icon")
    elif points <= -1:
        point_classification = "likely_benign"
        temperature_icon = TEMPERATURE_STRINGS[-1].get("icon")
    elif points <= 5:
        point_classification = "uncertain_significance"
    elif points <= 9:
        point_classification = "likely_pathogenic"
        temperature_icon = TEMPERATURE_STRINGS[6].get("icon")
    elif points >= 10:
        point_classification = "pathogenic"
        temperature_icon = TEMPERATURE_STRINGS[6].get("icon")

    temperature_class = ACMG_COMPLETE_MAP[point_classification].get("color")
    temperature = ACMG_COMPLETE_MAP[point_classification].get("label")

    if point_classification == "uncertain_significance":
        temperature_class = TEMPERATURE_STRINGS[points].get("color")
        temperature = TEMPERATURE_STRINGS[points].get("label")
        temperature_icon = TEMPERATURE_STRINGS[points].get("icon")

    return {
        "points": points,
        "temperature": temperature,
        "temperature_class": temperature_class,
        "temperature_icon": temperature_icon,
        "point_classification": ACMG_COMPLETE_MAP[point_classification].get("short"),
    }


def get_acmg_conflicts(acmg_terms: set) -> list:
    """Check potential conflict paris, return list of reference strings."""

    conflicts = []
    for t1, t2, reference in ACMG_POTENTIAL_CONFLICTS:
        if t1 in acmg_terms and t2 in acmg_terms:
            conflicts.append(reference)

    return conflicts
