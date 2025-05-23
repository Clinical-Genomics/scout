from scout.utils.acmg import (
    get_acmg,
    get_acmg_conflicts,
    get_acmg_temperature,
    is_benign,
    is_likely_benign,
    is_likely_pathogenic,
    is_pathogenic,
)


def test_is_pathogenic_1():
    """First criterias for pathogenic:

    Pathogenic
      (i) 1 Very strong (PVS1) AND
        (a) ≥1 Strong (PS1–PS4) OR
        (b) ≥2 Moderate (PM1–PM6) OR
        (c) 1 Moderate (PM1–PM6) and 1 supporting (PP1–PP5) OR
        (d) ≥2 Supporting (PP1–PP5)

    """
    # GIVEN values that fulfill the (a) criteria for pathogenic
    pvs = ["PVS1"]
    ps_terms = ["PS1"]
    pm_terms = []
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    ps_terms = []
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res

    ps_terms = ["PS1", "PS2"]
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert res

    # GIVEN values that fulfill the (b) criteria for pathogenic
    pvs = ["PVS1"]
    ps_terms = []
    pm_terms = ["PM1", "PM2"]
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    ## GIVEN one to few moderate terms
    pm_terms = ["PM2"]
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res

    # GIVEN values that fulfill the (c) criteria for pathogenic
    pvs = ["PVS1"]
    ps_terms = []
    pm_terms = ["PM1"]
    pp_terms = ["PP1"]
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    # GIVEN values that fulfill the (d) criteria for pathogenic
    pvs = ["PVS1"]
    ps_terms = []
    pm_terms = []
    pp_terms = ["PP1", "PP2"]
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    ## GIVEN pvs and one supporting term
    pp_terms = ["PP1"]
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res


def test_is_pathogenic_2():
    """First criterias for pathogenic:

    Pathogenic
      (ii) ≥2 Strong (PS1–PS4) OR

    """
    # GIVEN values that fulfill the (ii) criteria for pathogenic
    pvs = []
    ps_terms = ["PS1", "PS2"]
    pm_terms = []
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    ps_terms = ["PS1"]
    ## WHEN performing the evaluation wit only one strong term
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res


def test_is_pathogenic_3():
    """First criterias for pathogenic:

    Pathogenic
      (iii) 1 Strong (PS1–PS4) AND
        (a)≥3 Moderate (PM1–PM6) OR
        (b)2 Moderate (PM1–PM6) AND ≥2 Supporting (PP1–PP5) OR
        (c)1 Moderate (PM1–PM6) AND ≥4 supporting (PP1–PP5)


    """
    # GIVEN values that fulfill the (a) criteria for pathogenic (iii)
    pvs = []
    ps_terms = ["PS1"]
    pm_terms = ["PM1", "PM2", "PM3"]
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pm_terms = ["PM1", "PM2"]
    ## WHEN performing the evaluation wit only two moderate terms
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res

    # GIVEN values that fulfill the (b) criteria for pathogenic (iii)
    pvs = []
    ps_terms = ["PS1"]
    pm_terms = ["PM1", "PM2"]
    pp_terms = ["PP1", "PP2"]
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pp_terms = ["PP1"]
    ## WHEN performing the evaluation with only one supporting terms
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res

    # GIVEN values that fulfill the (c) criteria for pathogenic (iii)
    pvs = []
    ps_terms = ["PS1"]
    pm_terms = ["PM1"]
    pp_terms = ["PP1", "PP2", "PP3", "PP4"]
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pp_terms = ["PP1", "PP2", "PP3"]
    ## WHEN performing the evaluation with only three supporting terms
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res


def test_is_likely_pathogenic_1():
    """First criterias for pathogenic:

    Pathogenic
      (i) 1 Very strong (PVS1) AND 1 moderate (PM1– PM6)

    """
    # GIVEN values that fulfill the (1) criteria for likely pathogenic
    pvs = ["PVS1"]
    ps_terms = []
    pm_terms = ["PM1"]
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pm_terms = []
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res


def test_is_likely_pathogenic_2():
    """First criterias for pathogenic:

    Pathogenic
      (ii) 1 Strong (PS1–PS4) AND 1–2 moderate (PM1–PM6) OR

    """
    # GIVEN values that fulfill the (1) criteria for likely pathogenic
    pvs = []
    ps_terms = ["PS1"]
    pm_terms = ["PM1"]
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    ps_terms = []
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res


def test_is_likely_pathogenic_3():
    """First criterias for pathogenic:

    Pathogenic
      (iii) 1 Strong (PS1–PS4) AND ≥2 supporting (PP1–PP5) OR

    """
    # GIVEN values that fulfill the (1) criteria for likely pathogenic
    pvs = []
    ps_terms = ["PS1"]
    pm_terms = []
    pp_terms = ["PP1", "PP2"]
    ## WHEN performing the evaluation
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pp_terms = ["PP1"]
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res


def test_is_likely_pathogenic_4():
    """First criterias for pathogenic:

    Pathogenic
      (iv)  ≥3 Moderate (PM1–PM6) OR

    """
    # GIVEN values that fulfill the (1) criteria for likely pathogenic
    pvs = []
    ps_terms = []
    pm_terms = ["PM1", "PM2", "PM3"]
    pp_terms = []
    ## WHEN performing the evaluation
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pm_terms = ["PM1", "PM2"]
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res


def test_is_likely_pathogenic_5():
    """First criterias for pathogenic:

    Pathogenic
      (v) 2 Moderate (PM1–PM6) AND ≥2 supporting (PP1–PP5) OR

    """
    # GIVEN values that fulfill the (1) criteria for likely pathogenic
    pvs = []
    ps_terms = []
    pm_terms = ["PM1", "PM2"]
    pp_terms = ["PP1", "PP2"]
    ## WHEN performing the evaluation
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pp_terms = ["PP1"]
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res


def test_is_likely_pathogenic_6():
    """First criterias for pathogenic:

    Pathogenic
      (vi) 1 Moderate (PM1–PM6) AND ≥4 supportin (PP1–PP5)

    """
    # GIVEN values that fulfill the (vi) criteria for likely pathogenic
    pvs = []
    ps_terms = []
    pm_terms = ["PM1"]
    pp_terms = ["PP1", "PP2", "PP3", "PP4"]
    ## WHEN performing the evaluation
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    pp_terms = ["PP1", "PP2", "PP3"]
    res = is_likely_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res


def test_is_benign_1():
    """First criterias for benign:

    Benign
      (i) 1 Stand-alone (BA1) OR

    """
    # GIVEN values that fulfill the (i) criteria for benign
    ba = ["BA1"]
    bs_terms = []
    ## WHEN performing the evaluation
    res = is_benign(ba, bs_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    ba = []
    res = is_benign(ba, bs_terms)
    assert not res


def test_is_benign_2():
    """Second criterias for benign:

    Benign
      (ii) ≥2 Strong (BS1–BS4)

    """
    # GIVEN values that fulfill the (ii) criteria for benign
    ba = []
    bs_terms = ["BS1", "BS2"]
    ## WHEN performing the evaluation
    res = is_benign(ba, bs_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    bs_terms = ["BS1"]
    res = is_benign(ba, bs_terms)
    assert not res


def test_is_likely_benign_1():
    """First criterias for likely benign:

    Likely Benign
      (i) 1 Strong (BS1–BS4) and 1 supporting (BP1– BP7) OR

    """
    # GIVEN values that fulfill the (i) criteria for likely benign
    bs_terms = ["BS1"]
    bp_terms = ["BP1"]
    ## WHEN performing the evaluation
    res = is_likely_benign(bs_terms, bp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    bp_terms = []
    res = is_likely_benign(bs_terms, bp_terms)
    assert not res


def test_is_benign_2():
    """Second criterias for likely benign:

    Benign
      (ii) ≥2 Supporting (BP1–BP7)

    """
    # GIVEN values that fulfill the (ii) criteria for likely benign
    bs_terms = []
    bp_terms = ["BP1", "BP2"]
    ## WHEN performing the evaluation
    res = is_likely_benign(bs_terms, bp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    bp_terms = ["BP1"]
    res = is_likely_benign(bs_terms, bp_terms)
    assert not res


def test_get_acmg_no_terms():
    acmg_terms = set()
    res = get_acmg(acmg_terms)
    assert res is None


def test_get_acmg_pathogenic():
    acmg_terms = {"PVS1", "PS1"}
    res = get_acmg(acmg_terms)
    assert res == "pathogenic"

    acmg_terms = {"PVS1", "PS1", "BS1"}
    res = get_acmg(acmg_terms)
    assert res == "pathogenic"


def test_get_acmg_modifier():
    acmg_terms = {"PVS1", "PS1"}
    res = get_acmg(acmg_terms)
    assert res == "pathogenic"

    acmg_terms = {"PVS1_Moderate", "PS1"}
    res = get_acmg(acmg_terms)
    assert res == "likely_pathogenic"


def test_get_acmg_uncertain():
    acmg_terms = {"PVS1"}
    res = get_acmg(acmg_terms)
    assert res == "uncertain_significance"

    acmg_terms = {"PVS1", "PS1", "BS1", "BS2"}
    res = get_acmg(acmg_terms)
    assert res == "uncertain_significance"


def test_get_acmg_stand_alone_benign():
    acmg_terms = {"PVS1", "PS1", "BA1"}
    res = get_acmg(acmg_terms)
    assert res == "benign"

    acmg_terms = {"BA1", "BS1", "BP1"}
    res = get_acmg(acmg_terms)
    assert res == "benign"


def test_acmg_modifier_on_both_benign_and_pathogenic():
    acmg_terms = {"PS3_Moderate", "PP1_Moderate", "PP3", "BS1_Supporting"}
    res = get_acmg(acmg_terms)
    assert res == "uncertain_significance"


def test_acmg_benign_moderate():
    acmg_terms = {"BP1_Moderate", "BS1"}
    res = get_acmg(acmg_terms)
    assert res == "likely_benign"


def test_acmg_conflicts():
    acmg_terms = {"PVS1", "PM4"}
    conflicts = get_acmg_conflicts(acmg_terms)
    assert len(conflicts) == 1


def test_acmg_temperature():
    acmg_terms = {"PVS1", "PS1", "PP1", "BS1", "BS2"}
    res = get_acmg_temperature(acmg_terms)
    assert res["points"] == 5
    assert res["temperature"] == "Hot"
    assert res["point_classification"] == "VUS"

    acmg_terms = {"PS3_Moderate", "PP1_Moderate", "PP3", "BS1_Supporting"}
    res = get_acmg_temperature(acmg_terms)
    assert res["points"] == 4
    assert res["temperature"] == "Warm"
    assert res["point_classification"] == "VUS"

    acmg_terms = {"PS1_Very Strong", "PP1_Moderate", "PP3", "BS1_Supporting"}
    res = get_acmg_temperature(acmg_terms)
    assert res["points"] == 10
    assert res["temperature"] == "Pathogenic"
    assert res["point_classification"] == "P"

    acmg_terms = {"PS1_Very Strong", "PP1_Moderate", "PP3", "BS1_Supporting", "BS2_Stand-alone"}
    res = get_acmg_temperature(acmg_terms)
    assert res["points"] == 2
    assert res["temperature"] == "Cold"
    assert res["point_classification"] == "VUS"

    acmg_terms = {"PVS1", "BS2", "BP1"}
    res = get_acmg_temperature(acmg_terms)
    assert res["points"] == 3
    assert res["temperature"] == "Tepid"
    assert res["point_classification"] == "VUS"
