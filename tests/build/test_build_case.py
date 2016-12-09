# -*- coding: utf-8 -*-
from scout.build import build_case

def test_build_case(parsed_case):
    #GIVEN a parsed case
    #WHEN bulding a case model
    case_obj = build_case(parsed_case)
    #THEN make sure it is built in the proper way
    assert case_obj.case_id == parsed_case['case_id']
    assert len(case_obj.individuals) == len(parsed_case['individuals'])
