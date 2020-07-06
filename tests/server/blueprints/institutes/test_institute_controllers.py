import copy
from scout.server.blueprints.institutes.controllers import cases


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
    data = cases(store=adapter, case_query=all_cases, prioritized_cases_query=prio_cases, limit=1)

    # THEN 2 cases should be returned
    assert data["found_cases"] == 2


def test_controller_cases(adapter):
    # GIVEN an adapter with a case
    dummy_case = {
        "case_id": "1",
        "owner": "cust000",
        "individuals": [
            {"analysis_type": "wgs", "sex": 1, "phenotype": 2, "individual_id": "ind1"}
        ],
        "status": "inactive",
    }
    adapter.case_collection.insert_one(dummy_case)
    case_query = adapter.case_collection.find()
    # WHEN fetching a case with the controller
    data = cases(adapter, case_query)
    # THEN
    assert isinstance(data, dict)
    assert data["found_cases"] == 1
