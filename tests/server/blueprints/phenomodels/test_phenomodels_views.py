import datetime

from flask import url_for
from flask_login import current_user

from scout.server.extensions import store

TEST_SUBPANEL = dict(
    title="Subp title",
    subtitle="Subp subtitle",
    created=datetime.datetime.now(),
    updated=datetime.datetime.now(),
)

PHENOMODELS_REDIRECT_URL = "scout.server.blueprints.institutes.views.redirect"
PHENOMODEL_URL = "phenomodels.phenomodel"
PHENOMODEL_EDIT_URL = "phenomodels.phenomodel_edit"
PHENOMODELS_CHECKBOX_EDIT_URL = "phenomodels.checkbox_edit"
TEST_MODEL_NAME = "Test model"
TEST_MODEL_DESC = "Test model description"


def test_create_phenomodel(app, institute_obj):
    """Test the view showing the available phenotype models for an institute, after sending POST request with new phenotype model data"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        form_data = dict(model_name=TEST_MODEL_NAME, model_desc=TEST_MODEL_DESC)

        # WHEN user creates a new phenotype model using the phenomodel page
        resp = client.post(
            url_for(
                "phenomodels.create_phenomodel",
                institute_id=institute_obj["internal_id"],
            ),
            data=form_data,
        )
        # THEN page should redirect
        assert resp.status_code == 302
        # AND a phenomodel should have been created
        assert store.phenomodel_collection.find_one()


def test_remove_phenomodel(app, institute_obj, mocker, mock_redirect):
    """Testing the endpoint to remove an existing phenotype model for an institute"""

    mocker.patch(PHENOMODELS_REDIRECT_URL, return_value=mock_redirect)

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
    model_obj = store.phenomodel_collection.find_one()
    assert model_obj

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        form_data = {"model_id": model_obj["_id"]}

        # WHEN the user removes the model via the remove_phenomodel endpoint
        client.post(
            url_for("phenomodels.remove_phenomodel", institute_id=institute_obj["internal_id"]),
            data=form_data,
        )
        # THEN the phenotype model should be deleted from the database
        assert store.phenomodel_collection.find_one() is None


def test_phenomodel_get(app, institute_obj):
    """test the phenomodel page endpoint, GET request"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
    model_obj = store.phenomodel_collection.find_one()

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))
        # THEN the phenomodel endpoint should shown phenotype model info
        resp = client.get(
            url_for(
                PHENOMODEL_URL,
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            )
        )
        assert TEST_MODEL_NAME in str(resp.data)


def test_phenomodel_lock(app, institute_obj, mocker, mock_redirect):
    """Test the endpoint to lock a phenomodel and make it editable only by admins"""

    mocker.patch(PHENOMODELS_REDIRECT_URL, return_value=mock_redirect)

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
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
            url_for("phenomodels.lock_phenomodel"),
            data=form_data,
        )
        # Then the page should redirect
        assert resp.status_code == 302
        # And current user + admins emails will be registered as the emails of the admins
        locked_model = store.phenomodel_collection.find_one()
        assert locked_model["admins"] == [current_user.email] + admins


def test_phenomodel_unlock(app, institute_obj, mocker, mock_redirect):
    """Test the endpoint to unlock a phenomodel and make it editable only by all users"""

    mocker.patch(PHENOMODELS_REDIRECT_URL, return_value=mock_redirect)

    # GIVEN an institute with phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
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
            url_for("phenomodels.lock_phenomodel"),
            data=form_data,
        )
        # Then the page should redirect
        assert resp.status_code == 302
        # And the model will have no admins
        unlocked_model = store.phenomodel_collection.find_one()
        assert unlocked_model["admins"] == []


def test_phenomodel_rename_model(app, institute_obj):
    """Test the phenomodel endpoing, POST request for updating model info"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], "Old model", "Old description")
    model_obj = store.phenomodel_collection.find_one()

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # WHEN the user updates model info using a POST request
        form_data = dict(
            update_model="update", model_name="New model", model_desc="New description"
        )
        client.post(
            url_for(
                PHENOMODEL_EDIT_URL,
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
    # THEN the model in the database should be updated
    updated_model = store.phenomodel_collection.find_one()
    assert updated_model["name"] == "New model"


def test_phenomodel_add_delete_subpanel(app, institute_obj):
    """Test the phenomodel endpoint, by sending requests for adding and deleting a subpanel"""
    # GIVEN an institute with a phenotype model having no subpanels
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
    model_obj = store.phenomodel_collection.find_one()
    assert model_obj["subpanels"] == {}

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        form_data = dict(
            title="Phenotype subpanel title",
            subtitle="Phenotype subpanel subtitle",
            add_subpanel="Save phenotype subpanel",
        )
        # WHEN the user creates subpanel in phenotype model via POST request
        client.post(
            url_for(
                PHENOMODEL_EDIT_URL,
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
        client.post(
            url_for(
                PHENOMODEL_EDIT_URL,
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
        # THEN the model should be removed from models subpanels
        updated_model = store.phenomodel_collection.find_one()
        assert updated_model["subpanels"] == {}


def test_phenomodel_post_add_hpo_checkbox_to_subpanel(app, institute_obj, hpo_checkboxes):
    """Test adding an HPO checkbox with its children to a subpanel of a phenotype model via POST request"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
    model_obj = store.phenomodel_collection.find_one()
    # containing a subpanel
    model_obj["subpanels"] = {"subpanel_x": TEST_SUBPANEL}
    store.update_phenomodel(model_obj["_id"], model_obj)

    # GIVEN a database with the required HPO terms (one parent term and one child term)
    store.hpo_term_collection.insert_many(hpo_checkboxes)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        client.get(url_for("auto_login"))

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
        client.post(
            url_for(
                PHENOMODELS_CHECKBOX_EDIT_URL,
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


def test_phenomodel_post_add_disease_checkbox_to_subpanel(
    app, institute_obj, test_omim_database_term
):
    """Test adding a disease checkbox to a subpanel of a phenotype model via POST request"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
    model_obj = store.phenomodel_collection.find_one()
    # containing a subpanel
    model_obj["subpanels"] = {"subpanel_x": TEST_SUBPANEL}
    store.update_phenomodel(model_obj["_id"], model_obj)

    # GIVEN a database with the required disease term
    store.disease_term_collection.insert_one(test_omim_database_term)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # WHEN the user creates a disease checkbox using the endpoint
        form_data = dict(
            disease_subpanel_id="subpanel_x",
            diseaseHasTitle="on",
            diseaseTermTitle="Title for term",
            disease_term=" | ".join(
                [test_omim_database_term["_id"], test_omim_database_term["description"]]
            ),
            disease_custom_name="Alternative disease name",
            add_disease="",
        )
        client.post(
            url_for(
                PHENOMODELS_CHECKBOX_EDIT_URL,
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
        # THEN the disease term should have been added to the subpanel checkboxes and include correct data
        updated_model = store.phenomodel_collection.find_one()
        checkbox = updated_model["subpanels"]["subpanel_x"]["checkboxes"][
            test_omim_database_term["_id"]
        ]
        assert checkbox["name"] == test_omim_database_term["_id"]
        assert checkbox["checkbox_type"] == test_omim_database_term["source"].lower()
        assert checkbox["description"] == test_omim_database_term["description"]
        assert checkbox["term_title"] == form_data["diseaseTermTitle"]
        assert checkbox["custom_name"] == form_data["disease_custom_name"]


def test_phenomodel_post_remove_subpanel_checkbox(app, institute_obj):
    """Test removing a single checkbox from a phenotype model subpanel"""

    # GIVEN an institute with a phenotype model
    store.create_phenomodel(institute_obj["internal_id"], TEST_MODEL_NAME, TEST_MODEL_DESC)
    model_obj = store.phenomodel_collection.find_one()
    # containing a subpanel with a checkbox
    TEST_SUBPANEL["checkboxes"] = {"HP:000001": {"name": "HP:000001"}}
    model_obj["subpanels"] = {"subpanel_x": TEST_SUBPANEL}
    store.update_phenomodel(model_obj["_id"], model_obj)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # WHEN the user removes the checkbox using the endpoint, POST request
        form_data = dict(checkgroup_remove="#".join(["HP:000001", "subpanel_x"]))
        client.post(
            url_for(
                PHENOMODELS_CHECKBOX_EDIT_URL,
                institute_id=institute_obj["internal_id"],
                model_id=model_obj["_id"],
            ),
            data=form_data,
        )
    # THEN the checkbox should be removed from the subpanel
    updated_model = store.phenomodel_collection.find_one()
    assert updated_model["subpanels"]["subpanel_x"]["checkboxes"] == {}
