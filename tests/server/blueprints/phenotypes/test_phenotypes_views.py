# -*- coding: utf-8 -*-
from flask import url_for


def test_phenotypes(app, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the phenotypes page
        resp = client.get(url_for("phenotypes.hpo_terms"))

        # THEN it should return a page
        assert resp.status_code == 200


def test_phenotypes_api(app, real_adapter, hpo_term):
    adapter = real_adapter
    # GIVEN a database with an HPO term
    adapter.load_hpo_term(hpo_term)

    with app.test_client() as client:
        # WHEN retrieving json for all HPO terms
        resp = client.get(url_for("phenotypes.api_hpo_terms"))

        # THEN the response should be JSON
        assert resp.content_type == "application/json"


def test_phenotypes_api(app, real_adapter, hpo_term):
    adapter = real_adapter
    # GIVEN a database with an HPO term
    adapter.load_hpo_term(hpo_term)

    with app.test_client() as client:
        # WHEN retrieving json for all HPO terms
        resp = client.get(url_for("phenotypes.api_hpo_term_search", search_string="Leukemia"))

        # THEN the response should be JSON
        assert resp.content_type == "application/json"


# Needs a populated hpo db..
# def test_search_phenotypes(app, real_variant_database):
# GIVEN an initialized app
# GIVEN a valid user and institute
#    adapter = real_variant_database

#    with app.test_client() as client:
# GIVEN that the user could be logged in
#        resp = client.get(url_for('auto_login'))
#        assert resp.status_code == 200

# GIVEN an HPO-term in the database
#        hpo_term = adapter.hpo_term_collection.find_one()
#        assert hpo_term

#        hpo_query = hpo_term['hpo_id']
#        assert hpo_query

# WHEN searching the phenotypes page
#        resp = client.post(url_for('phenotypes.hpo_terms', hpo_term=hpo_query))

# THEN it should return a page
#        assert resp.status_code == 200
# that contains the search term
#        assert hpo_term.encode() in resp.data
