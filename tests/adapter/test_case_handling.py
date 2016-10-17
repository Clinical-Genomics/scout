import pytest
import logging

from scout.models import Case

from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)

def test_add_cases(adapter, case_obj, institute_obj):
    assert adapter.cases().count() == 0
    adapter.add_institute(institute_obj)
    adapter.add_case(case_obj)
    
    result = adapter.cases()
    
    for case in result:
        assert case.owner == case_obj.owner
        
    logger.info("All cases checked")

def test_add_existing_case(adapter, case_obj, institute_obj):
    assert adapter.cases().count() == 0
    adapter.add_institute(institute_obj)
    
    adapter.add_case(case_obj)
    with pytest.raises(IntegrityError):
        adapter.add_case(case_obj)

def test_get_case(adapter, case_obj, institute_obj):
    assert adapter.cases().count() == 0
    adapter.add_institute(institute_obj)
    adapter.add_case(case_obj)
    logger.info("Testing to get case")

    result = adapter.case(
        institute_id=case_obj.owner,
        case_id=case_obj.display_name
    )
    assert result.owner == case_obj.owner

def test_add_user(adapter, institute_obj, parsed_user):
    adapter.add_institute(institute_obj)
    adapter.getoradd_user(
        email=parsed_user['email'], 
        name=parsed_user['name'],
        location=parsed_user['location'], 
        institutes=parsed_user['institutes']
    )
    assert adapter.user(email=parsed_user['email']).name == parsed_user['name']

#
# def test_update_case(setup_database, get_case_info):
#     print('')
#     logger.info("Add a case")
#
#     setup_database.add_case(
#         case_lines=get_case_info['case_lines'],
#         case_type=get_case_info['case_type'],
#         owner=get_case_info['owner'],
#         scout_configs=get_case_info['scout_configs']
#     )
#
#     result = setup_database.case(
#         institute_id='cust000',
#         case_id='636808'
#     )
#
#     assert result.owner == 'cust000'
#     assert set(result.collaborators) == set(['cust000'])
#
#     logger.info("Set case in research mode")
#     result['is_research'] = True
#     result.save()
#
#     logger.info("Update case info")
#     get_case_info['scout_configs']['collaborators'] = ['cust001']
#
#     setup_database.add_case(
#         case_lines=get_case_info['case_lines'],
#         case_type=get_case_info['case_type'],
#         owner=get_case_info['owner'],
#         scout_configs=get_case_info['scout_configs']
#     )
#
#     result = setup_database.case(
#         institute_id='cust000',
#         case_id='636808'
#     )
#
#     assert set(result.collaborators) == set(['cust000', 'cust001'])
#     assert result.is_research == True
#
#     logger.info("Removing case")
#     result.delete()
#
#
#