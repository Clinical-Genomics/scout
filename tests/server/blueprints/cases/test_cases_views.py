# -*- coding: utf-8 -*-
from flask import url_for

def test_cases(app, user_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for('cases.cases',
                                  institute_id=institute_obj['internal_id']))

        # THEN it should return a page
        assert resp.status_code == 200

def test_cases_query(app, user_obj, case_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    slice_query = case_obj['display_name']

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(url_for('cases.cases',
                                  query=slice_query,
                                  institute_id=institute_obj['internal_id']))

        # THEN it should return a page
        assert resp.status_code == 200

def test_cases_panel_query(app, user_obj, case_obj, parsed_panel, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    slice_query = parsed_panel['panel_id']

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(url_for('cases.cases',
                                  query=slice_query,
                                  institute_id=institute_obj['internal_id']))

        # THEN it should return a page
        assert resp.status_code == 200

def test_institutes(app, user_obj):
    # GIVEN an initialized app
    # GIVEN a valid user

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the institutes page
        resp = client.get(url_for('cases.index'))

        # THEN it should return a page
        assert resp.status_code == 200

def test_case(app, user_obj, case_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user, case and institute

        with app.test_client() as client:
            # GIVEN that the user could be logged in
            resp = client.get(url_for('auto_login'))
            assert resp.status_code == 200

            # WHEN accessing the case page
            resp = client.get(url_for('cases.case',
                                      institute_id=institute_obj['internal_id'],
                                      case_name=case_obj['display_name']))

            # THEN it should return a page
            assert resp.status_code == 200

def test_causatives(app, user_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

        with app.test_client() as client:
            # GIVEN that the user could be logged in
            resp = client.get(url_for('auto_login'))
            assert resp.status_code == 200

            # WHEN accessing the case page
            resp = client.get(url_for('cases.causatives',
                                      institute_id=institute_obj['internal_id']))

            # THEN it should return a page
            assert resp.status_code == 200
