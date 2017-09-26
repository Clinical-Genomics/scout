

def test_update_caseid(real_oldcase_database, scout_config):
    # GIVEN a case with a "old-style" case id
    adapter = real_oldcase_database['adapter']
    old_case = real_oldcase_database['case']
    old_caseid = old_case['_id']
    assert old_caseid == '-'.join([old_case['owner'], old_case['display_name']])
    assert isinstance(adapter.case(old_caseid), dict)
    assert adapter.case(scout_config['family']) is None

    case_lists = {'suspects': None, 'causatives': None}
    for case_variants in case_lists:
        case_lists[case_variants] = old_case[case_variants][0]
        assert isinstance(adapter.variant(case_lists[case_variants]), dict)

    old_variant = real_oldcase_database['variant']
    old_evaluation = adapter.get_evaluations(old_variant)[0]
    assert old_evaluation['case_id'] == old_caseid
    assert old_evaluation['variant_specific'] == old_variant['_id']

    institute_obj = adapter.institute(old_case['owner'])
    events = adapter.events(institute_obj, case=old_case)
    for event_obj in events:
        assert event_obj['case'] == old_caseid

    # WHEN updating the case it as part of a upload
    adapter.load_case(scout_config, update=True)

    # THEN it should replace the case in the database
    assert adapter.case(old_caseid) is None
    new_case = adapter.case(scout_config['family'])
    assert isinstance(new_case, dict)
    # AND the suspect/causative variant should have an updated id
    for case_variants, old_variantid in case_lists.items():
        assert new_case[case_variants][0] != old_variantid
        assert isinstance(adapter.variant(new_case[case_variants][0]), dict)
    # AND the ACMG classification should have new case + variant ids
    new_variant = adapter.variants(new_case['_id'])[0]
    new_evaluation = adapter.get_evaluations(new_variant)[0]
    assert new_evaluation['case_id'] == new_case['_id']
    assert new_evaluation['variant_specific'] == new_variant['_id']
    # AND update ids for events
    assert adapter.events(institute_obj, case=old_case).count() == 0
    new_events = adapter.events(institute_obj, case=new_case)
    for event_obj in new_events:
        assert event_obj['case'] == new_case['_id']
