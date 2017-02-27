# -*- coding: utf-8 -*-
import pytest
import logging

from pprint import pprint as pp

from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)

def test_add_cases(institute_database, case_obj):
    adapter = institute_database
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find().count() == 0
    
    ## WHEN adding a new case to the database
    adapter.add_case(case_obj)

    ## THEN it should be populated with the new case
    result = adapter.cases()
    assert result.count() == 1
    for case in result:
        assert case['owner'] == case_obj['owner']

    logger.info("All cases checked")


def test_add_existing_case(institute_database, case_obj):
    adapter = institute_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0

    adapter.add_case(case_obj)
    ## WHEN adding a existing case to the database
    with pytest.raises(IntegrityError):
    ## THEN it should raise integrity error
        adapter.add_case(case_obj)

def test_get_case(institute_database, case_obj):
    adapter = institute_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    logger.info("Testing to get case")

    ## WHEN retreiving an existing case from the database
    result = adapter.case(case_id=case_obj['case_id'])
    ## THEN we should get the correct case
    assert result['owner'] == case_obj['owner']

def test_get_non_existing_case(institute_database, case_obj):
    adapter = institute_database
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.add_case(case_obj)
    logger.info("Testing to get case")

    # WHEN retreiving an non existing case from the database
    result = adapter.case(case_id='hello')
    # THEN we should get None back
    assert result is None

