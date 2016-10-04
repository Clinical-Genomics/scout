from scout.ext.backend.utils import get_mongo_case

def test_get_case(get_case_info):
    case_lines = get_case_info['case_lines']
    owner = get_case_info['scout_configs']['owner']
    
    case_obj = get_mongo_case(case_lines, owner)
    
    assert case_obj.owner == owner