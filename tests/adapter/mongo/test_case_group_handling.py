import pytest
import copy
import pymongo
import logging

from bson.objectid import ObjectId

logger = logging.getLogger(__name__)


def test_init_case_group(adapter, institute_obj):
    # given a database and an institute
    owner = institute_obj["_id"]

    # when attempting to create a case group
    result = adapter.init_case_group(owner)

    # the result is ok
    assert result


def test_remove_case_group(adapter, institute_obj):
    # given a database and an institute
    owner = institute_obj["_id"]

    # when successfully creating a case group
    resulting_id = adapter.init_case_group(owner)
    assert resulting_id

    # when removing it again
    result = adapter.remove_case_group(resulting_id)

    # the result is ok
    assert result


def test_cases_group_query(adapter, case_obj):
    # given a database and a case

    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    ## WHEN inserting an object with a group id
    group_id = ObjectId("101010101010101010101010")
    case_obj["group"] = [group_id]
    adapter.case_collection.insert_one(case_obj)

    # THEN that case is returned when asking for the group
    cases = adapter.cases(group=group_id)
    case_ids = [case["_id"] for case in cases]

    assert case_obj["_id"] in case_ids
