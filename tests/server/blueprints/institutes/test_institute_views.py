# -*- coding: utf-8 -*-
import datetime

import pytest
from flask import url_for
from flask_login import current_user

from scout.server.extensions import store

TEST_SUBPANEL = dict(
    title="Subp title",
    subtitle="Subp subtitle",
    created=datetime.datetime.now(),
    updated=datetime.datetime.now(),
)


def test_advanced_phenotypes_POST(app, user_obj, institute_obj):
    """Test the view showing the available phenotype models for an institute, after sending POST request with new phenotype model data"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        form_data = dict(model_name="A test model", model_desc="Test model description")

        # WHEN user creates a new phenotype model using the phenomodel page
        resp = client.post(
            url_for(
                "overview.advanced_phenotypes",
                institute_id=institute_obj["internal_id"],
            ),
            data=form_data,
        )
        assert resp.status_code == 200
        # THEN the new model should be visible in the page
        assert form_data["model_name"] in str(resp.data)


def test_remove_phenomodel(app, user_obj, institute_obj, mocker, mock_redirect):
    """Testing the endpoint to remove an existing phenotype model for an institute"""

    mocker.patch("scout.server.blueprints.institutes.views.redirect", return_value=mock_redirect)

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model_obj = store.phenomodel_collection.find_one()
    assert model_obj

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        form_data = {"model_id": model_obj["_id"]}

        # WHEN the user removes the model via the remove_phenomodel endpoint
        resp = client.post(
            url_for("overview.remove_phenomodel", institute_id=institute_obj["internal_id"]),
            data=form_data,
        )
        # THEN the phenotype model should be deleted from the database
        assert store.phenomodel_collection.find_one() is None


def test_phenomodel_GET(app, user_obj, institute_obj):
    """test the phenomodel page endpoint, GET request"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model_obj = store.phenomodel_collection.find_one()

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        # THEN the phenomodel endpoint should shown phenotype model info
        resp = client.get(
            url_for(
                "overview.phenomodel",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            )
        )
        assert "Test model" in str(resp.data)


def test_phenomodel_lock(app, user_obj, institute_obj, mocker, mock_redirect):
    """Test the endpoint to lock a phenomodel and make it editable only by admins"""

    mocker.patch("scout.server.blueprints.institutes.views.redirect", return_value=mock_redirect)

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model = store.phenomodel_collection.find_one()
    assert "admins" not in model

    admins = ["user1@email", "user2@email"]

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # WHEN the user locks model up using two admins
        form_data = dict(model_id=model["_id"], lock="", user_admins=admins)
        resp = client.post(
            url_for("overview.lock_phenomodel"),
            data=form_data,
        )
        # Then the page should redirect
        assert resp.status_code == 302
        # And current user + admins emails will be registered as the emails of the admins
        locked_model = store.phenomodel_collection.find_one()
        assert locked_model["admins"] == [current_user.email] + admins


def test_phenomodel_unlock(app, user_obj, institute_obj, mocker, mock_redirect):
    """Test the endpoint to unlock a phenomodel and make it editable only by all users"""

    mocker.patch("scout.server.blueprints.institutes.views.redirect", return_value=mock_redirect)

    # GIVEN an institute with phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model = store.phenomodel_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))
        # Given that the phenomodel is locked and current user is admin
        model["admins"] = [current_user.email]
        store.update_phenomodel(model["_id"], model)
        locked_model = store.phenomodel_collection.find_one()
        assert locked_model["admins"] == [current_user.email]

        # When the test_phenomodel_lock endpoint is used to unlock the model
        form_data = dict(
            model_id=model["_id"],
        )
        resp = client.post(
            url_for("overview.lock_phenomodel"),
            data=form_data,
        )
        # Then the page should redirect
        assert resp.status_code == 302
        # And the model will have no admins
        unlocked_model = store.phenomodel_collection.find_one()
        assert unlocked_model["admins"] == []


def test_phenomodel_POST_rename_model(app, user_obj, institute_obj):
    """Test the phenomodel endpoing, POST request for updating model info"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Old model", "Old description")
    model_obj = store.phenomodel_collection.find_one()

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN the user updates model info using a POST request
        form_data = dict(
            update_model="update", model_name="New model", model_desc="New description"
        )
        resp = client.post(
            url_for(
                "overview.phenomodel",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
    # THEN the model in the database should be updated
    updated_model = store.phenomodel_collection.find_one()
    assert updated_model["name"] == "New model"


def test_phenomodel_POST_add_delete_subpanel(app, user_obj, institute_obj):
    """Test the phenomodel endpoint, by sending requests for adding and deleting a subpanel"""
    # GIVEN an institute with a phenotype model having no subpanels
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model_obj = store.phenomodel_collection.find_one()
    assert model_obj["subpanels"] == {}

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        form_data = dict(
            title="Phenotype subpanel title",
            subtitle="Phenotype subpanel subtitle",
            add_subpanel="Save phenotype subpanel",
        )
        # WHEN the user creates subpanel in phenotype model via POST request
        resp = client.post(
            url_for(
                "overview.phenomodel",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
        # Then the subpanel dictionary should be added to model subpanels
        updated_model = store.phenomodel_collection.find_one()
        subpanel_id = list(updated_model["subpanels"].keys())[0]
        assert updated_model["subpanels"][subpanel_id]["title"] == "Phenotype subpanel title"
        assert updated_model["subpanels"][subpanel_id]["subtitle"] == "Phenotype subpanel subtitle"

        # WHEN the user sends a POST request to remove the subpanel
        form_data = dict(subpanel_delete=subpanel_id)
        resp = client.post(
            url_for(
                "overview.phenomodel",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
        # THEN the model should be removed from models subpanels
        updated_model = store.phenomodel_collection.find_one()
        assert updated_model["subpanels"] == {}


def test_phenomodel_POST_add_omim_checkbox_to_subpanel(app, user_obj, institute_obj, omim_checkbox):
    """Test adding an OMIM checkbox to a subpanel of a phenotype model via POST request"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model_obj = store.phenomodel_collection.find_one()
    # containing a subpanel
    model_obj["subpanels"] = {"subpanel_x": TEST_SUBPANEL}
    store.update_phenomodel(model_obj["_id"], model_obj)
    model_obj = store.phenomodel_collection.find_one()
    assert model_obj["subpanels"]["subpanel_x"]

    # GIVEN that database contains the HPO term to add to the subopanel
    store.disease_term_collection.insert_one(omim_checkbox)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        # WHEN the user creates an OMIM checkbox using the endpoint
        form_data = dict(
            omim_subpanel_id="subpanel_x",
            omimHasTitle="on",
            omimTermTitle="Title for term",
            omim_term=" | ".join([omim_checkbox["_id"], omim_checkbox["description"]]),
            omim_custom_name="Alternative OMIM name",
            add_omim="",
        )
        resp = client.post(
            url_for(
                "overview.checkbox_edit",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
        # THEN the term should have been added to the subpanel checkboxe
        updated_model = store.phenomodel_collection.find_one()
        checkbox = updated_model["subpanels"]["subpanel_x"]["checkboxes"]["OMIM:121210"]
        assert checkbox["name"] == "OMIM:121210"
        assert checkbox["checkbox_type"] == "omim"
        assert checkbox["description"] == "Febrile seizures familial 1"
        assert checkbox["term_title"] == form_data["omimTermTitle"]
        assert checkbox["custom_name"] == form_data["omim_custom_name"]


def test_phenomodel_POST_add_hpo_checkbox_to_subpanel(app, user_obj, institute_obj, hpo_checkboxes):
    """Test adding an HPO checkbox with its children to a subpanel of a phenotype model via POST request"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model_obj = store.phenomodel_collection.find_one()
    # containing a subpanel
    model_obj["subpanels"] = {"subpanel_x": TEST_SUBPANEL}
    store.update_phenomodel(model_obj["_id"], model_obj)

    # GIVEN a database with the required HPO terms (one parent term and one child term)
    store.hpo_term_collection.insert_many(hpo_checkboxes)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        # WHEN the user creates an HPO checkbox using the endpoint
        form_data = dict(
            hpo_subpanel_id="subpanel_x",
            hpoHasTitle="on",
            hpoTermTitle="Title for term",
            hpo_term=" | ".join([hpo_checkboxes[0]["_id"], hpo_checkboxes[0]["description"]]),
            hpo_custom_name="Alternative HPO name",
            add_hpo="",
            includeChildren="on",
        )
        resp = client.post(
            url_for(
                "overview.checkbox_edit",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
        # THEN the term should have been added to the subpanel checkboxes
        updated_model = store.phenomodel_collection.find_one()
        checkbox = updated_model["subpanels"]["subpanel_x"]["checkboxes"]["HP:0025190"]
        assert checkbox["name"] == "HP:0025190"
        assert checkbox["checkbox_type"] == "hpo"
        assert checkbox["description"] == "Bilateral tonic-clonic seizure with generalized onset"
        assert checkbox["term_title"] == form_data["hpoTermTitle"]
        assert checkbox["custom_name"] == form_data["hpo_custom_name"]
        # Additionally, the HPO term checkbox should contain a nested HPO term:
        nested_hpo_term = {
            "name": hpo_checkboxes[1]["_id"],
            "description": hpo_checkboxes[1]["description"],
        }
        assert checkbox["children"] == [nested_hpo_term]


def test_phenomodel_POST_remove_subpanel_checkbox(app, user_obj, institute_obj):
    """Test removing a single checkbox from a phenotype model subpanel"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Test model", "Model description")
    model_obj = store.phenomodel_collection.find_one()
    # containing a subpanel with a checkbox
    TEST_SUBPANEL["checkboxes"] = {"HP:000001": {"name": "HP:000001"}}
    model_obj["subpanels"] = {"subpanel_x": TEST_SUBPANEL}
    store.update_phenomodel(model_obj["_id"], model_obj)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        # WHEN the user removes the checkbox using the endpoint, POST request
        form_data = dict(checkgroup_remove="#".join(["HP:000001", "subpanel_x"]))
        resp = client.post(
            url_for(
                "overview.checkbox_edit",
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
    # THEN the checkbox should be removed from the subpanel
    updated_model = store.phenomodel_collection.find_one()
    assert updated_model["subpanels"]["subpanel_x"]["checkboxes"] == {}


def test_overview(app, user_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for("overview.institutes"))

        # THEN it should return a page
        assert resp.status_code == 200


def test_institute_settings(app, user_obj, institute_obj):
    """Test function that creates institute update form and updates an institute"""

    # GIVEN a gene panel
    test_panel = store.panel_collection.find_one()
    assert test_panel

    # AND 2 mock HPO terms in database
    mock_disease_terms = [
        {"_id": "HP:0001298", "description": "Encephalopathy", "hpo_id": "HP:0001298"},
        {"_id": "HP:0001250", "description": "Seizures", "hpo_id": "HP:0001250"},
    ]
    for term in mock_disease_terms:
        store.load_hpo_term(term)
        assert store.hpo_term(term["_id"])

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:

        client.get(url_for("auto_login"))

        # WHEN accessing the cases page (GET method)
        resp = client.get(
            url_for("overview.institute_settings", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200

        # WHEN updating an institute using the following form
        form_data = {
            "display_name": "updated name",
            "sanger_emails": ["john@doe.com"],
            "coverage_cutoff": "15",
            "frequency_cutoff": "0.001",
            "cohorts": ["test cohort 1", "test cohort 2"],
            "institutes": ["cust111", "cust222"],
            "pheno_groups": [
                "HP:0001298 , Encephalopathy ( ENC )",
                "HP:0001250 , Seizures ( EP )",
            ],
            "gene_panels": [test_panel["panel_name"]],
            "alamut_key": "test_alamut_key",
        }

        # via POST request
        resp = client.post(
            url_for("overview.institute_settings", institute_id=institute_obj["internal_id"]),
            data=form_data,
        )
        assert resp.status_code == 200

        # THEN the institute object should be updated with the provided form data
        updated_institute = store.institute_collection.find_one()
        assert updated_institute["display_name"] == form_data["display_name"]
        assert updated_institute["sanger_recipients"] == form_data["sanger_emails"]
        assert updated_institute["coverage_cutoff"] == int(form_data["coverage_cutoff"])
        assert updated_institute["frequency_cutoff"] == float(form_data["frequency_cutoff"])
        assert updated_institute["cohorts"] == form_data["cohorts"]
        assert updated_institute["collaborators"] == form_data["institutes"]
        assert len(updated_institute["phenotype_groups"]) == 2  # one for each HPO term
        assert updated_institute["gene_panels"] == {
            test_panel["panel_name"]: test_panel["display_name"]
        }
        assert updated_institute["alamut_key"] == form_data["alamut_key"]


def test_cases(app, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for("overview.cases", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200

        # test query passing parameters in seach form
        request_data = {
            "limit": "100",
            "skip_assigned": "on",
            "is_research": "on",
            "query": "case_id",
        }
        resp = client.get(
            url_for(
                "overview.cases",
                institute_id=institute_obj["internal_id"],
                params=request_data,
            )
        )
        # response should return a page
        assert resp.status_code == 200

        sorting_options = ["analysis_date", "track", "status"]
        for option in sorting_options:
            # test query passing the sorting option to the cases view
            request_data = {"sort": option}
            resp = client.get(
                url_for(
                    "overview.cases",
                    institute_id=institute_obj["internal_id"],
                    params=request_data,
                )
            )
            # response should return a page
            assert resp.status_code == 200


def test_cases_query_case_name(app, case_obj, institute_obj):
    """Test cases filtering by case display name"""

    slice_query = f"case:{case_obj['display_name']}"

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_panel_query(app, case_obj, parsed_panel, institute_obj):
    """Test cases filtering by gene panel"""

    slice_query = f"panel:{parsed_panel['panel_id']}"

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_by_pinned_gene_query(app, case_obj, institute_obj):
    """Test cases filtering by providing the gene of one of its pinned variants"""

    # GIVEN a test variant hitting POT1 gene (hgnc_id:17284)
    suspects = []
    test_variant = store.variant_collection.find_one({"genes.hgnc_id": {"$in": [17284]}})
    assert test_variant

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # GIVEN a case with this variant pinned
        form = {
            "action": "ADD",
        }
        client.post(
            url_for(
                "cases.pin_variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=test_variant["_id"],
            ),
            data=form,
        )
        updated_case = store.case_collection.find_one({"suspects": {"$in": [test_variant["_id"]]}})
        assert updated_case

        # WHEN the case search is performed using the POT1 gene
        slice_query = f"pinned:POT1"

        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_exact_phenotype_query(app, case_obj, institute_obj, test_hpo_terms):
    """Test cases filtering by providing one HPO term"""

    # GIVEN a case with some HPO terms
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
    )
    one_hpo_term = test_hpo_terms[0]["phenotype_id"]
    slice_query = f"exact_pheno:{one_hpo_term}"

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with the query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_similar_phenotype_query(app, case_obj, institute_obj, test_hpo_terms):
    """Test cases filtering by providing HPO terms that are related to case phenotype"""

    # GIVEN a case with some HPO terms
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
    )

    # WHEN similar but distinct HPO terms are used in the query
    similar_hpo_terms = ["HP:0012047", "HP:0000618"]
    for term in test_hpo_terms:
        assert term["phenotype_id"] not in similar_hpo_terms

    similar_hpo_terms = ",".join(similar_hpo_terms)
    slice_query = f"similar_pheno:{similar_hpo_terms}"

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with the query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_causatives(app, user_obj, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    # There should be no causative variants for test case:
    assert "causatives" not in case_obj
    var1_id = "4c7d5c70d955875504db72ef8e1abe77"  # in POT1 gene
    var2_id = "e24b65bf27feacec6a81c8e9e19bd5f1"  # in TBX1 gene
    var_ids = [var1_id, var2_id]

    # for each variant
    for var_id in var_ids:
        # update case by marking variant as causative:
        variant_obj = store.variant(document_id=var_id)
        store.mark_causative(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="causative_var_link/{}".format(variant_obj["_id"]),
            variant=variant_obj,
        )
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    # The above variants should be registered as causatives in case object
    assert updated_case["causatives"] == var_ids

    # Call scout causatives view and check if the above causatives are displayed
    with app.test_client() as client:

        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.get(url_for("overview.causatives", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # and variant 2
        assert var2_id in str(resp.data)

        # Filter causatives by gene (POT1)
        resp = client.get(
            url_for(
                "overview.causatives",
                institute_id=institute_obj["internal_id"],
                query="17284 | POT1 (DKFZp586D211, hPot1, POT1)",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # but NOT variant 2
        assert var2_id not in str(resp.data)


def test_gene_variants_filter(app, institute_obj, case_obj):
    """Test the function that allows searching SNVs and INDELS using filters"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When user submits a query for a variants in a specific gene and a rank score
        filter_query = {
            "hgnc_symbols": "POT1",
            "variant_type": ["clinical"],
            "rank_score": 11,
        }

        resp = client.post(
            url_for("overview.gene_variants", institute_id=institute_obj["internal_id"]),
            data=filter_query,
        )
        # THEN it should return a page
        assert resp.status_code == 200

        # containing  variants in that genes
        assert "POT1" in str(resp.data)


def test_gene_variants_no_valid_gene(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test the gene_variant endpoint with a gene symbol not in database"""

    mocker.patch("scout.server.blueprints.institutes.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When user submits a query for a variants in a gene that is not in database
        filter_query = {
            "hgnc_symbols": "UNKNOWN-GENE",
            "variant_type": ["clinical"],
            "rank_score": 11,
        }

        resp = client.post(
            url_for("overview.gene_variants", institute_id=institute_obj["internal_id"]),
            data=filter_query,
        )
        # THEN the page should redirect
        assert resp.status_code == 302


def test_institute_users(app, institute_obj, user_obj):
    """Test the link to all institute users"""
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN accessing the cases page
        resp = client.get(
            url_for("overview.institute_users", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200

        # Containing the test user's name
        assert user_obj["name"] in str(resp.data)


def test_filters(app, institute_obj, user_obj, case_obj, filter_obj):
    """Test the link to all institute users"""
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        category = "snv"
        filter_id = store.stash_filter(filter_obj, institute_obj, case_obj, user_obj, category)
        store.lock_filter(filter_id, user_obj.get("email"))

        # WHEN accessing the cases page
        resp = client.get(url_for("overview.filters", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200

        # Containing the test user's name
        assert user_obj["name"] in str(resp.data)


def test_clinvar_submissions(app, institute_obj, clinvar_variant, clinvar_casedata):
    """Test the web page containing the clinvar submissions for an institute"""

    # GIVEN an institute with a clinvar submission
    store.create_submission(institute_obj["_id"])
    open_submission = store.get_open_clinvar_submission(institute_obj["_id"])
    submission_with_data = store.add_to_submission(
        open_submission["_id"], ([clinvar_variant], [clinvar_casedata])
    )
    assert submission_with_data

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When visiting the clinvar submission page (get request)
        resp = client.get(
            url_for(
                "overview.clinvar_submissions",
                institute_id=institute_obj["internal_id"],
            )
        )

        # a successful response should be returned
        assert resp.status_code == 200
        assert str(submission_with_data["_id"]) in str(resp.data)


def test_rename_clinvar_samples(app, institute_obj, clinvar_variant, clinvar_casedata):
    """Test the form button triggering the renaming of samples for a clinvar submission"""

    # GIVEN an institute with a clinvar submission
    store.create_submission(institute_obj["_id"])
    open_submission = store.get_open_clinvar_submission(institute_obj["_id"])
    submission_with_data = store.add_to_submission(
        open_submission["_id"], ([clinvar_variant], [clinvar_casedata])
    )
    assert submission_with_data["_id"]

    # GIVEN an initialized app and a valid user
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        case_id = clinvar_casedata["case_id"]
        old_name = clinvar_casedata["individual_id"]

        form_data = dict(
            new_name="new_sample_name",
        )

        referer = url_for("overview.clinvar_submissions", institute_id=institute_obj["internal_id"])

        # WHEN the sample name is edited from the submission page (POST request)
        resp = client.post(
            url_for(
                f"overview.clinvar_rename_casedata",
                submission=submission_with_data["_id"],
                case=case_id,
                old_name=old_name,
            ),
            data=form_data,
            headers={"referer": referer},
        )
        # a successful response should be redirect to the submssions page
        assert resp.status_code == 302

        # And the sample name should have been updated in the database
        updated_casedata = store.clinvar_collection.find_one({"_id": clinvar_casedata["_id"]})
        assert updated_casedata["individual_id"] != clinvar_casedata["individual_id"]
