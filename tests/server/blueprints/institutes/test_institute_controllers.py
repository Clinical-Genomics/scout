import copy
from werkzeug.datastructures import MultiDict
from scout.server.extensions import store

from scout.server.blueprints.institutes.controllers import cases, phenomodel_checkgroups_filter

HPO_TERMS = [
    {
        "_id": "HP:0025190",
        "hpo_id": "HP:0025190",
        "description": "Bilateral tonic-clonic seizure with generalized onset",
        "children": ["HP:0032661"],
        "ancestors": [],
    },
    {
        "_id": "HP:0032661",
        "hpo_id": "HP:0032661",
        "description": "Generalized convulsive status epilepticus",
        "children": [],
        "ancestors": ["HP:0025190"],
    },
]
OMIM_TERM = {
    "_id": "OMIM:121210",
    "description": "Febrile seizures familial 1",
}


def test_phenomodel_checkgroups_filter(app, institute_obj):
    """Test the controllers function that updates the phenotype model based on the model preview checkbox preferences"""
    # GIVEN a database with the required HPO terms (one parent term and one child term)
    store.hpo_term_collection.insert_many(HPO_TERMS)

    # GIVEN a phenotype model with one panel and 3 checkboxes (checkbox2 nested inside checkbox1)
    hpo_id1 = HPO_TERMS[0]["_id"]
    hpo_id2 = HPO_TERMS[1]["_id"]
    omim_id = OMIM_TERM["_id"]
    checkbox2 = dict(
        name=hpo_id2,
        description=HPO_TERMS[1]["description"],
    )
    checkbox1 = dict(
        name=hpo_id1,
        description=HPO_TERMS[1]["description"],
        children=[checkbox2],  # nested checkbox with HPO term 2
    )
    checkbox3 = {"name": omim_id, "description": OMIM_TERM["description"]}
    test_model = dict(
        institute=institute_obj["_id"],
        name="Test model",
        subpanels=dict(panel1=dict(checkboxes={hpo_id1: checkbox1, omim_id: checkbox3})),
    )
    store.phenomodel_collection.insert_one(test_model)
    model_obj = store.phenomodel_collection.find_one()
    # THEN 2 checkboxes should show at the top level
    assert model_obj["subpanels"]["panel1"]["checkboxes"][hpo_id1]
    assert model_obj["subpanels"]["panel1"]["checkboxes"][omim_id]
    assert hpo_id2 not in model_obj["subpanels"]["panel1"]["checkboxes"]

    with app.app_context():
        # WHEN phenotype checkboxes are updated to keep only the nested checkbox2
        checked_terms = MultiDict({"cheked_terms": [".".join(["panel1", hpo_id1, hpo_id2])]})
        updated_model = phenomodel_checkgroups_filter(model_obj, checked_terms)
        # THEN the right checkbox should be present in submodel checkboxes dictionary
        assert updated_model["subpanels"]["panel1"]["checkboxes"][hpo_id2]
        assert hpo_id1 not in updated_model["subpanels"]["panel1"]["checkboxes"]
        assert omim_id not in updated_model["subpanels"]["panel1"]["checkboxes"]


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
