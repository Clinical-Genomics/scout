# -*- coding: utf-8 -*-
from flask import url_for

from scout.server.extensions import store


def test_omim_diagnosis(app, test_omim_database_term):
    """Test page that displays an OMIM diagnosis info"""

    # GIVEN a database with at least one gene
    store.disease_term_collection.insert_one(test_omim_database_term)

    # GIVEN an initialized app
    with app.test_client() as client:
        # WHEN accessing the page of one OMIM diagnosis
        resp = client.get(
            url_for("diagnoses.diagnosis", disease_id=test_omim_database_term["disease_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_omim_diagnosis_api(app, test_omim_database_term):
    """Test page that displays an OMIM diagnosis info"""

    store.load_disease_term(test_omim_database_term)

    with app.test_client() as client:
        # WHEN asking for a list of all disorders
        response = client.get(url_for("diagnoses.api_diagnoses"))

        # THEN a json response is returned
        assert response.content_type == "application/json"
