import pytest
import copy
import pymongo
import logging

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
