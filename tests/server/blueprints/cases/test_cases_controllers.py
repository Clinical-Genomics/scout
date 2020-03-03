"""Tests for the cases controllers"""
import copy

from flask import Flask

from scout.server.blueprints.cases.controllers import case, case_report_content, cases


def test_cases(adapter, case_obj, institute_obj):

    # GIVEN a non prioritized case
    case = case_obj
    assert case["status"] == "inactive"
    adapter.case_collection.insert_one(case)

    # GIVEN a priotized case
    case2 = copy.deepcopy(case)
    case2["_id"] = "internal_id2"
    case2["status"] = "prioritized"
    adapter.case_collection.insert_one(case2)

    all_cases = adapter.cases(collaborator=institute_obj["_id"])
    assert len(list(all_cases)) == 2

    prio_cases = adapter.prioritized_cases(institute_id=institute_obj["_id"])
    assert len(list(prio_cases)) == 1

    all_cases = adapter.cases(collaborator=institute_obj["_id"])
    prio_cases = adapter.prioritized_cases(institute_id=institute_obj["_id"])

    # WHEN the cases controller is invoked
    data = cases(
        store=adapter, case_query=all_cases, prioritized_cases_query=prio_cases, limit=1
    )

    # THEN 2 cases should be returned
    assert data["found_cases"] == 2


def test_case_report_content(adapter, institute_obj, case_obj, variant_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.variant_collection.insert_one(variant_obj)
    ## GIVEN an adapter with a case that have an existing causative
    case_obj = adapter.case_collection.find_one()
    institute_obj = adapter.institute_collection.find_one()
    var_obj = adapter.variant_collection.find_one({"case_id": case_obj["_id"]})
    assert var_obj
    case_obj["causatives"] = [var_obj["_id"]]
    ## WHEN fetching a case with the controller
    data = case_report_content(adapter, institute_obj, case_obj)
    ## THEN assert the result is on the correct format
    assert isinstance(data, dict)
    variant_types = {
        "causatives_detailed": "causatives",
        "suspects_detailed": "suspects",
        "classified_detailed": "acmg_classification",
        "tagged_detailed": "manual_rank",
        "tier_detailed": "cancer_tier",
        "dismissed_detailed": "dismiss_variant",
        "commented_detailed": "is_commented",
    }
    for var_type in variant_types:
        if var_type == "causatives_detailed":
            assert len(data[var_type]) == 1
            continue
        assert len(data[var_type]) == 0


def test_cases_controller(adapter, dummy_case):
    # GIVEN an adapter with a case
    adapter.case_collection.insert_one(dummy_case)
    case_query = adapter.case_collection.find()
    # WHEN fetching a case with the controller
    data = cases(adapter, case_query)
    # THEN
    assert isinstance(data, dict)
    assert data["found_cases"] == 1


def test_case_controller_rank_model_link(adapter, institute_obj, dummy_case):
    # GIVEN an adapter with a case
    dummy_case["rank_model_version"] = "1.3"
    adapter.case_collection.insert_one(dummy_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    app.config["RANK_MODEL_LINK_PREFIX"] = "http://"
    app.config["RANK_MODEL_LINK_POSTFIX"] = ".ini"
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that the link has been added
    assert "rank_model_link" in fetched_case


def test_case_controller(adapter, institute_obj, dummy_case):
    # GIVEN an adapter with a case
    adapter.case_collection.insert_one(dummy_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that the case have no link
    assert "rank_model_link" not in fetched_case


def test_case_controller_no_panels(adapter, institute_obj, dummy_case):
    # GIVEN an adapter with a case without gene panels
    adapter.case_collection.insert_one(dummy_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    assert "panel_names" not in fetched_case
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN
    assert fetched_case["panel_names"] == []


def test_case_controller_with_panel(adapter, institute_obj, panel, dummy_case):
    # GIVEN an adapter with a case with a gene panel
    dummy_case["panels"] = [
        {
            "panel_name": panel["panel_name"],
            "version": panel["version"],
            "nr_genes": 2,
            "is_default": True,
        }
    ]
    adapter.case_collection.insert_one(dummy_case)
    adapter.institute_collection.insert_one(institute_obj)
    # GIVEN an adapter with a gene panel
    adapter.panel_collection.insert_one(panel)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that the display information has been added to case
    assert len(fetched_case["panel_names"]) == 1


def test_case_controller_panel_wrong_version(adapter, institute_obj, panel, dummy_case):
    # GIVEN an adapter with a case with a gene panel with wrong version
    dummy_case["panels"] = [
        {
            "panel_name": panel["panel_name"],
            "version": panel["version"] + 1,
            "nr_genes": 2,
            "is_default": True,
        }
    ]
    adapter.case_collection.insert_one(dummy_case)
    adapter.institute_collection.insert_one(institute_obj)
    # GIVEN an adapter with a gene panel
    adapter.panel_collection.insert_one(panel)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that it succeded to fetch another panel version
    assert str(panel["version"]) in fetched_case["panel_names"][0]


def test_case_controller_non_existing_panel(adapter, institute_obj, dummy_case, panel):
    # GIVEN an adapter with a case with a gene panel but no panel objects
    dummy_case["panels"] = [
        {
            "panel_name": panel["panel_name"],
            "version": panel["version"] + 1,
            "nr_genes": 2,
            "is_default": True,
        }
    ]
    adapter.case_collection.insert_one(dummy_case)
    adapter.institute_collection.insert_one(institute_obj)
    fetched_case = adapter.case_collection.find_one()
    app = Flask(__name__)
    # WHEN fetching a case with the controller
    with app.app_context():
        data = case(adapter, institute_obj, fetched_case)
    # THEN assert that it succeded to fetch another panel version
    assert len(fetched_case["panel_names"]) == 0
