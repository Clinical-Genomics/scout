from scout.server.blueprints.cases.controllers import (case, cases, case_report_content)


def test_case_report_content(adapter, institute_obj, case_obj, variant_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.variant_collection.insert_one(variant_obj)
    ## GIVEN an adapter with a case that have an existing causative
    case_obj = adapter.case_collection.find_one()
    institute_obj = adapter.institute_collection.find_one()
    var_obj = adapter.variant_collection.find_one({'case_id': case_obj['_id']})
    assert var_obj    
    case_obj['causatives'] = [var_obj['_id']]
    ## WHEN fetching a case with the controller
    data = case_report_content(adapter, institute_obj, case_obj)
    ## THEN assert the result is on the correct format
    assert isinstance(data, dict)
    variant_types = {
        'causatives_detailed': 'causatives',
        'suspects_detailed': 'suspects',
        'classified_detailed': 'acmg_classification',
        'tagged_detailed': 'manual_rank',
        'dismissed_detailed': 'dismiss_variant',
        'commented_detailed': 'is_commented',
    }
    for var_type in variant_types:
        if var_type == 'causatives_detailed':
            assert len(data[var_type]) == 1
            continue
        assert len(data[var_type]) == 0


def test_case_controller(adapter):
    ## GIVEN an adapter with a case
    case_obj = {
        'case_id': '1',
        'individuals': [
            {'analysis_type': 'wgs'},
        ],
        'status': 'inactive',
    }
    adapter.case_collection.insert_one(case_obj)
    case_query = adapter.case_collection.find()
    ## WHEN fetching a case with the controller
    data = cases(adapter, case_query)
    ## THEN
    assert isinstance(data, dict)
    assert data['found_cases'] == 1


def test_cases_controller(adapter, institute_obj):
    ## GIVEN an adapter with a case
    case_obj = {
        'case_id': '1',
        'owner': 'cust000',
        'individuals': [
            {'analysis_type': 'wgs', 'sex': 1, 'phenotype': 2, 'individual_id': 'ind1'},
        ],
        'status': 'inactive',
    }
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    ## WHEN fetching a case with the controller
    data = case(adapter, institute_obj, fetched_case)
    ## THEN
    assert isinstance(data, dict)
    