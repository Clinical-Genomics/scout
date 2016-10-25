# -*- coding: utf-8 -*-
import pytest
import logging

from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)


def test_add_cases(adapter, case_obj, institute_obj):
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
