import pytest

from scout.load.report import load_report
from scout.exceptions import (IntegrityError, ValidationError)

def test_load_report(adapter):
    ## GIVEN a database with a case without case report
    case_id = 'test_case'
    case = {'_id':case_id}
    
    adapter._add_case(case)
    
    case_obj = adapter.case_collection.find_one()
    
    delivery_path = 'here'
    
    assert 'delivery_report' not in case_obj
    
    ## WHEN loading a delivery report
    updated_case = load_report(adapter, case_id, delivery_path)
    
    ## THEN assert the report is there
    
    assert updated_case['delivery_report'] == delivery_path

def test_load_report_non_existing_case(adapter):
    ## GIVEN a database with a case without case report
    case_id = 'test_case'
    case = {'_id':case_id}
    
    adapter._add_case(case)
    
    case_obj = adapter.case_collection.find_one()
    
    delivery_path = 'here'
    
    assert 'delivery_report' not in case_obj
    
    ## WHEN trying to load a delivery report in a non existing case
    with pytest.raises(IntegrityError):
        ## THEN assert an integrity error is raised
        updated_case = load_report(adapter, 'non existing case', delivery_path)

def test_load_report_existing_report(adapter):
    ## GIVEN a database with a case with case report
    case_id = 'test_case'
    delivery_path = 'here'
    
    case = {
        '_id':case_id,
        'delivery_report': delivery_path
    }
    
    adapter._add_case(case)
    
    case_obj = adapter.case_collection.find_one()
    
    assert 'delivery_report' in case_obj

    other_report = 'there'
    
    ## WHEN trying to load a delivery report in a case that already have a report
    with pytest.raises(ValidationError):
        ## THEN assert an validation error is raised
        updated_case = load_report(adapter, case_id, other_report)


def test_load_report_existing_update(adapter):
    ## GIVEN a database with a case with case report
    case_id = 'test_case'
    delivery_path = 'here'
    
    case = {
        '_id':case_id,
        'delivery_report': delivery_path
    }
    
    adapter._add_case(case)
    
    case_obj = adapter.case_collection.find_one()
    
    assert 'delivery_report' in case_obj

    other_report = 'there'
    
    ## WHEN trying to load a delivery report in a case that already have a report using update
    updated_case = load_report(adapter, case_id, other_report, update=True)
    
    ## THEN assert an validation error is raised
    assert updated_case['delivery_report'] == other_report

