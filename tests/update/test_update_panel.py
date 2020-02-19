from pprint import pprint as pp

from scout.update.panel import update_panel
from scout.utils.date import get_date


def test_update_panel_version(adapter, case_obj, dummypanel_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.panel_collection.insert_one(dummypanel_obj)

    ## GIVEN an adapter with a case with gene panels
    case_obj = adapter.case_collection.find_one()
    panel_obj = adapter.panel_collection.find_one()
    assert case_obj
    assert panel_obj

    case_id = case_obj["_id"]

    # There is information about a panel both in the panel collection
    # and on the case object. This is fine until one starts to manipulate the objects
    panel = case_obj["panels"][0]

    panel_version = panel["version"]
    panel_name = panel["panel_name"]
    panel_id = panel["panel_id"]

    new_panel_version = panel_version + 1

    ## WHEN updating the panel version
    update_panel(adapter, panel_name, panel_version, new_panel_version)

    ## THEN assert that the panel version was updated for the panel object
    updated_panel_obj = adapter.panel_collection.find_one(
        {"panel_name": panel_name, "version": new_panel_version}
    )

    assert updated_panel_obj["version"] == new_panel_version

    case_obj = adapter.case_collection.find_one({"_id": case_id})

    for panel in case_obj["panels"]:
        assert panel["version"] == new_panel_version


def test_update_panel_date(adapter, case_obj, dummypanel_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.panel_collection.insert_one(dummypanel_obj)

    ## GIVEN an adapter with a case with gene panels
    new_date_obj = get_date("2015-03-12")

    case_obj = adapter.case_collection.find_one()
    panel_obj = adapter.panel_collection.find_one()

    case_id = case_obj["_id"]

    # There is infirmation about a panel both in the panel collection
    # and on the case object. This is fine until one starts to manipulate the objects
    case_panel = case_obj["panels"][0]

    panel_version = case_panel["version"]
    panel_name = case_panel["panel_name"]
    panel_id = case_panel["panel_id"]

    ## WHEN updating the panel version

    update_panel(adapter, panel_name, panel_version=None, new_date=new_date_obj)

    ## THEN assert that the panel version was updated both in panel and case

    updated_panel_obj = adapter.panel_collection.find_one(
        {"panel_name": panel_name, "version": panel_version}
    )

    assert updated_panel_obj["date"] == new_date_obj

    case_obj = adapter.case_collection.find_one({"_id": case_id})

    for panel in case_obj["panels"]:
        assert panel["updated_at"] == new_date_obj


def test_update_panel_version_multiple(adapter, case_obj, dummypanel_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.panel_collection.insert_one(dummypanel_obj)

    case_obj["_id"] = "test_2"
    # Add another case with same panels
    adapter.case_collection.insert_one(case_obj)

    ## GIVEN an adapter with a case with gene panels
    case_obj = adapter.case_collection.find_one()
    panel_obj = adapter.panel_collection.find_one()

    # There is infirmation about a panel both in the panel collection
    # and on the case object. This is fine until one starts to manipulate the objects
    panel = case_obj["panels"][0]

    panel_version = panel["version"]
    panel_name = panel["panel_name"]
    panel_id = panel["panel_id"]

    new_panel_version = panel_version + 1

    ## WHEN updating the panel version

    update_panel(adapter, panel_name, panel_version, new_panel_version)

    ## THEN assert that the panel version was updated both in panel and case

    updated_panel_obj = adapter.panel_collection.find_one(
        {"panel_name": panel_name, "version": new_panel_version}
    )

    assert updated_panel_obj["version"] == new_panel_version

    for case_obj in adapter.case_collection.find():

        for panel in case_obj["panels"]:
            assert panel["version"] == new_panel_version
