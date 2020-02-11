# -*- coding: utf-8 -*-
from flask import url_for
from scout.server.extensions import store
from flask_wtf import FlaskForm as form


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


def test_institute(app, user_obj, institute_obj, monkeypatch):
    """Test function that creates institute update form and updates an institute"""

    # monkeypatching form validation is easier than haldling a missing csfr token
    def mock_validate_form(*args, **kwargs):
        return True

    monkeypatch.setattr(form, "validate_on_submit", mock_validate_form)

    # insert 2 mock HPO terms in database, for later use
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
            url_for("overview.institute", institute_id=institute_obj["internal_id"])
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
        }

        # via POST request
        resp = client.post(
            url_for("overview.institute", institute_id=institute_obj["internal_id"]),
            data=form_data,
        )
        assert resp.status_code == 200

        # THEN the institute object should be updated with the provided form data
        updated_institute = store.institute_collection.find_one()
        assert updated_institute["display_name"] == form_data["display_name"]
        assert updated_institute["sanger_recipients"] == form_data["sanger_emails"]
        assert updated_institute["coverage_cutoff"] == int(form_data["coverage_cutoff"])
        assert updated_institute["frequency_cutoff"] == float(
            form_data["frequency_cutoff"]
        )
        assert updated_institute["cohorts"] == form_data["cohorts"]
        assert updated_institute["collaborators"] == form_data["institutes"]
        assert len(updated_institute["phenotype_groups"]) == 2  # one for each HPO term
