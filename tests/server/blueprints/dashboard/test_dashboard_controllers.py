from pprint import pprint as pp

from scout.server.blueprints.dashboard.controllers import get_dashboard_info


def test_empty_database(real_adapter):
    ## GIVEN an empty database
    adapter = real_adapter
    ## WHEN asking for data
    data = get_dashboard_info(adapter)
    ## THEN assert that the data is empty
    assert data.get('total_cases') == 0

def test_one_case(real_adapter, case_obj):
    ## GIVEN an database with one case
    adapter = real_adapter
    adapter._add_case(case_obj)
    ## WHEN asking for data
    data = get_dashboard_info(adapter)
    ## THEN assert there is one case in the data
    for group in data['cases']:
        if group['status'] == 'all':
            assert group['count'] == 1
        elif group['status'] == case_obj['status']:
            assert group['count'] == 1

def test_one_causative(real_adapter, case_obj):
    ## GIVEN an database with two cases where one has a causative
    adapter = real_adapter
    adapter._add_case(case_obj)
    case_obj['causatives'] = ['a variant']
    case_obj['_id'] = 'test1'
    adapter._add_case(case_obj)
    ## WHEN asking for data
    institute_id = case_obj['owner']
    data = get_dashboard_info(adapter, institute_id=institute_id)
    ## THEN assert there is one case in the causative information
    for info in data['overview']:
        if info['title'] == 'Causative variants':
            assert info['count'] == 1
        else:
            assert info['count'] == 0