from scout.utils.acmg import is_pathogenic


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
    pvs = True
    ps_terms = ['PS1']
    pm_terms = []
    pp_terms  = []
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res
    
    ps_terms = []
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert not res

    ps_terms = ['PS1', 'PS2']
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    assert res
    
    
    # GIVEN values that fulfill the (b) criteria for pathogenic
    pvs = True
    ps_terms = []
    pm_terms = ['PM1', 'PM2']
    pp_terms  = []
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res
    
    ## GIVEN one to few moderate terms
    pm_terms = ['PM2']
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are not fullfilled
    assert not res

    # GIVEN values that fulfill the (c) criteria for pathogenic
    pvs = True
    ps_terms = []
    pm_terms = ['PM1']
    pp_terms  = ['PP1']
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res

    # GIVEN values that fulfill the (d) criteria for pathogenic
    pvs = True
    ps_terms = []
    pm_terms = []
    pp_terms  = ['PP1', 'PP2']
    ## WHEN performing the evaluation
    res = is_pathogenic(pvs, ps_terms, pm_terms, pp_terms)
    ## THEN assert the criterias are fullfilled
    assert res
    
    