# -*- coding: utf-8 -*-
from flask import url_for, current_app
from scout.server.extensions import store

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


def test_matchmaker_add(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.post(url_for('cases.matchmaker_add',
                                institute_id=institute_obj['internal_id'],
                                case_name=case_obj['display_name']))
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302


def test_matchmaker_matches(app, institute_obj, case_obj, mme_submission):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # add MME submission to case object
        store.case_collection.find_one_and_update(
            {'_id' : case_obj['_id']},
            {'$set' : {
                'mme_submission' : mme_submission
            }}
        )
        assert store.case_collection.find({'mme_submission':{'$exists' : True}}).count() == 1

        # Given mock MME connection parameters
        current_app.config['MME_URL'] = 'http://fakey_mme_url:fakey_port'
        current_app.config['MME_TOKEN'] = 'test_token'

        # WHEN accessing the case page
        resp = client.get(url_for('cases.matchmaker_matches',
                                institute_id=institute_obj['internal_id'],
                                case_name=case_obj['display_name']))

        # page will redirect because controllers.mme_matches
        # will not be able to contact a MME server
        assert resp.status_code == 302


def test_matchmaker_match(app, institute_obj, case_obj, mme_submission):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # add MME submission to case object
        store.case_collection.find_one_and_update(
            {'_id' : case_obj['_id']},
            {'$set' : {
                'mme_submission' : mme_submission
            }}
        )
        assert store.case_collection.find({'mme_submission':{'$exists' : True}}).count() == 1

        # WHEN accessing the case page
        resp = client.post(url_for('cases.matchmaker_match',
                                institute_id=institute_obj['internal_id'],
                                case_name=case_obj['display_name'],
                                target='mock_node_id' ))
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302


def test_matchmaker_delete(app, institute_obj, case_obj, mme_submission):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # add MME submission to case object
        store.case_collection.find_one_and_update(
            {'_id' : case_obj['_id']},
            {'$set' : {
                'mme_submission' : mme_submission
            }}
        )
        assert store.case_collection.find({'mme_submission':{'$exists' : True}}).count() == 1

        # WHEN accessing the case page
        resp = client.post(url_for('cases.matchmaker_delete',
                                institute_id=institute_obj['internal_id'],
                                case_name=case_obj['display_name']))
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302
