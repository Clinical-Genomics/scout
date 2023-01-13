# coding=UTF-8
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


def get_acmg(acmg_terms):
    """Use the algorithm described in ACMG paper to get a ACMG calssification

    Modifying strength of a term is possible by adding a string describing its new level: "PP1_Strong" or
    "PVS1_Moderate".

    If no terms return None

    Args:
        acmg_terms(set(str)): A collection of prediction terms

    Returns:
        prediction(str): in ['uncertain_significance','benign','likely_benign',
                             'likely_pathogenic','pathogenic']

    """
    if not acmg_terms:
        return None
    prediction = "uncertain_significance"
    # This variable indicates if Pathogenecity Very Strong exists
    pvs = False
    # Collection of terms with Pathogenecity Strong
    ps_terms = []
    # Collection of terms with Pathogenecity moderate
    pm_terms = []
    # Collection of terms with Pathogenecity supporting
    pp_terms = []
    # This variable indicates if Benign impact stand-alone exists
    ba = False
    # Collection of terms with Benign evidence Strong
    bs_terms = []
    # Collection of terms with supporting Benign evidence
    bp_terms = []
    for term in acmg_terms:
        if term.endswith("_Strong"):
            ps_terms.append(term)
        elif term.endswith("_Moderate"):
            pm_terms.append(term)
        elif term.endswith("_Supporting"):
            pp_terms.append(term)
        elif term.startswith("PVS"):
            pvs = True
        elif term.startswith("PS"):
            ps_terms.append(term)
        elif term.startswith("PM"):
            pm_terms.append(term)
        elif term.startswith("PP"):
            pp_terms.append(term)
        elif term.startswith("BA"):
            ba = True
        elif term.startswith("BS"):
            bs_terms.append(term)
        elif term.startswith("BP"):
            bp_terms.append(term)

    # We need to start by checking for Pathogenecity
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
