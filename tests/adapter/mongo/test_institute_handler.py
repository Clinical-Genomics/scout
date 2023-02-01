import time
from datetime import datetime

import pytest

from scout.exceptions import IntegrityError


def test_add_institute(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute

    adapter.add_institute(institute_obj)

    ## THEN assert the institute has been inserted in the correct way
    res = adapter.institute_collection.find_one({"_id": institute_obj["internal_id"]})

    assert res["_id"] == institute_obj["internal_id"]
    assert res["internal_id"] == institute_obj["internal_id"]
    assert res["display_name"] == institute_obj["display_name"]
    assert type(res["updated_at"]) == type(datetime.now())
    # assert res['updated_at'] == institute_obj['updated_at']

    ## THEN assert defaults where set

    assert res["coverage_cutoff"] == institute_obj["coverage_cutoff"]
    assert res["frequency_cutoff"] == institute_obj["frequency_cutoff"]


def test_add_institute_twice(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding the institute twice

    adapter.add_institute(institute_obj)

    ## THEN assert an exception is raised

    with pytest.raises(IntegrityError):
        adapter.add_institute(institute_obj)


def test_fetch_institute(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute

    adapter.add_institute(institute_obj)

    ## THEN assert it gets returned in the proper way

    res = adapter.institute(institute_obj["internal_id"])

    assert res["_id"] == institute_obj["internal_id"]
    assert res["internal_id"] == institute_obj["internal_id"]


def test_fetch_non_existing_institute(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and trying to fetch another institute

    adapter.add_institute(institute_obj)

    ## THEN assert the adapter returns None

    institute_obj = adapter.institute(institute_id="non existing")

    assert institute_obj is None


def test_update_institute_sanger(adapter, institute_obj, user_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating it

    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    adapter.update_institute(
        internal_id=institute_obj["internal_id"], sanger_recipient=user_obj["email"]
    )

    ## THEN assert that the institute has been updated

    res = adapter.institute(institute_id=institute_obj["internal_id"])

    assert len(res["sanger_recipients"]) == len(institute_obj.get("sanger_recipients", [])) + 1

    ## THEN assert updated_at was updated

    assert res["updated_at"] > institute_obj["created_at"]


def test_update_institute_sanger_IntegrityError(adapter, institute_obj, user_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating it without sanger_recipients
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    ## THEN error is raised as integrety is broken
    with pytest.raises(IntegrityError):
        adapter.update_institute(
            internal_id=institute_obj["internal_id"], sanger_recipient="missing_email"
        )


def test_update_institute_sanger_loqusDB(adapter, institute_obj, user_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating it

    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    adapter.update_institute(
        internal_id=institute_obj["internal_id"],
        sanger_recipient=user_obj["email"],
        loqusdb_ids=["mockID"],
    )

    ## THEN assert that the institute has been updated

    res = adapter.institute(institute_id=institute_obj["internal_id"])

    assert len(res["sanger_recipients"]) == len(institute_obj.get("sanger_recipients", [])) + 1

    ## THEN assert updated_at was updated

    assert res["updated_at"] > institute_obj["created_at"]


def test_update_display_name(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating it
    adapter.add_institute(institute_obj)
    display_name = "Test"

    assert institute_obj["display_name"] != display_name

    updated_institute = adapter.update_institute(
        internal_id=institute_obj["internal_id"], display_name=display_name
    )

    ## THEN assert that the institute has been updated

    assert updated_institute["display_name"] == display_name


def test_update_institute_coverage_cutoff(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating it

    adapter.add_institute(institute_obj)

    new_cutoff = 12.0

    time.sleep(1)

    adapter.update_institute(internal_id=institute_obj["internal_id"], coverage_cutoff=new_cutoff)

    res = adapter.institute(institute_id=institute_obj["internal_id"])

    ## THEN assert that the coverage cutoff has been updated
    assert res["coverage_cutoff"] == new_cutoff

    ## THEN assert updated_at was updated

    assert res["updated_at"] > institute_obj["created_at"]


def test_update_institute_sanger_and_cutoff(adapter, institute_obj, user_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating it

    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    new_cutoff = 12.0
    new_mail = user_obj["email"]

    adapter.update_institute(
        internal_id=institute_obj["internal_id"],
        sanger_recipient=new_mail,
        coverage_cutoff=new_cutoff,
    )

    res = adapter.institute(institute_id=institute_obj["internal_id"])

    ## THEN assert that the coverage cutoff has been updated
    assert res["coverage_cutoff"] == new_cutoff

    ## THEN assert that the sanger recipients has been updated
    assert len(res["sanger_recipients"]) == len(institute_obj.get("sanger_recipients", [])) + 1

    ## THEN assert updated_at was updated

    assert res["updated_at"] > institute_obj["created_at"]


def test_updating_non_existing_institute(adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert sum(1 for i in adapter.institutes()) == 0

    ## WHEN adding a institute and updating the wrong one

    adapter.add_institute(institute_obj)

    ## THEN assert that the update did not add any institutes to the database
    assert sum(1 for i in adapter.institutes()) == 1

    with pytest.raises(IntegrityError):
        adapter.update_institute(internal_id="nom existing", sanger_recipient="john.doe@mail.com")
