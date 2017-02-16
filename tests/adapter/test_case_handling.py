# -*- coding: utf-8 -*-
import pytest
import logging

from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)


def test_add_cases(real_pymongo_adapter, case_obj, institute_obj):
    adapter = real_pymongo_adapter
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    # WHEN adding a new case to the database
    for ind in case_obj.individuals:
        print(ind.to_json())
    adapter.add_institute(institute_obj)
    adapter.add_case(case_obj)

    # THEN it should be populated with the new case
    result = adapter.cases()
    for case in result:
        assert case.owner == case_obj.owner

    logger.info("All cases checked")


def test_add_existing_case(real_pymongo_adapter, case_obj, institute_obj):
    adapter = real_pymongo_adapter
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.add_institute(institute_obj)

    adapter.add_case(case_obj)
    # WHEN adding a existing case to the database
    with pytest.raises(IntegrityError):
    # THEN it should raise integrity error
        adapter.add_case(case_obj)


def test_get_case(real_pymongo_adapter, case_obj, institute_obj):
    adapter = real_pymongo_adapter
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.add_institute(institute_obj)
    adapter.add_case(case_obj)
    logger.info("Testing to get case")

    # WHEN retreiving an existing case from the database
    result = adapter.case(
        institute_id=case_obj.owner,
        case_id=case_obj.display_name
    )
    # THEN we should get the correct case
    assert result.owner == case_obj.owner

def test_get_non_existing_case(real_pymongo_adapter, case_obj, institute_obj):
    adapter = real_pymongo_adapter
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.add_institute(institute_obj)
    adapter.add_case(case_obj)
    logger.info("Testing to get case")

    # WHEN retreiving an non existing case from the database
    result = adapter.case(
        institute_id=case_obj.owner,
        case_id='hello'
    )
    # THEN we should get None back
    assert result == None


def test_add_user(real_pymongo_adapter, institute_obj, parsed_user):
    adapter = real_pymongo_adapter
    # GIVEN an empty database (no users)
    assert adapter.user().count() == 0
    adapter.add_institute(institute_obj)
    # WHEN adding a user to the database
    adapter.getoradd_user(
        email=parsed_user['email'],
        name=parsed_user['name'],
        location=parsed_user['location'],
        institutes=parsed_user['institutes']
    )
    # THEN we should get the correct user
    assert adapter.user(email=parsed_user['email']).name == parsed_user['name']
