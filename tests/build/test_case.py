from scout.build import build_case

def test_build_minimal_case(parsed_case):
    case_obj = build_case(parsed_case)
    
    assert case_obj.case_id == parsed_case['case_id']
    assert len(case_obj.individuals) == 0