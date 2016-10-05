from scout.parse import parse_case

def test_parse_case(get_case_info):
    case_lines = get_case_info['case_lines']
    owner = get_case_info['scout_configs']['owner']
    
    case = parse_case(case_lines, owner)
    
    assert case['owner'] == owner