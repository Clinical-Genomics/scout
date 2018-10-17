from pprint import pprint as pp

from scout.server.blueprints.dashboard.controllers import get_case_info


def test_empty_database(real_adapter):
    ## GIVEN an empty database
    adapter = real_adapter
    ## WHEN asking for data
    data = get_case_info(adapter, total_cases=adapter.nr_cases())
    ## THEN assert that the data is empty
    assert data == {}

def test_one_case(real_adapter, case_obj):
    ## GIVEN an database with one case
    adapter = real_adapter
    adapter._add_case(case_obj)
    ## WHEN asking for data
    data = get_case_info(adapter, total_cases=adapter.nr_cases())
    ## THEN assert there is one case in the data
    for group in data['cases']:
        if group['status'] == 'all':
            assert group['count'] == 1
        elif group['status'] == case_obj['status']:
            assert group['count'] == 1

# def test_one_case(real_adapter, case_obj):
#     ## GIVEN an database with one case
#     adapter = real_adapter
#     adapter._add_case(case_obj)
#     ## WHEN asking for data
#     institute_id = case_obj['owner']
#     data = get_case_info(adapter, total_cases=adapter.nr_cases(), institute_id=institute_id)
#     ## THEN assert there is one case in the data
#     pp(data)
#     assert data == {}