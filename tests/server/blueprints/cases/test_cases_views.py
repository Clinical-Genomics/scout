# -*- coding: utf-8 -*-
from flask import url_for, current_app
from flask_login import current_user

from scout.server.extensions import store


def test_cases(app, institute_obj):
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

        # test query passing parameters in seach form
        request_data = {
            'limit' : '100',
            'skip_assigned' : 'on',
            'is_research' : 'on',
            'query' : 'case_id'
        }
        resp = client.get(url_for('cases.cases',
                                  institute_id=institute_obj['internal_id'], params=request_data))
        # response should return a page
        assert resp.status_code == 200

        sorting_options = ['analysis_date', 'track', 'status']
        for option in sorting_options:
            # test query passing the sorting option to the cases view
            request_data = {
                'sort' : option
            }
            resp = client.get(url_for('cases.cases',
                                      institute_id=institute_obj['internal_id'], params=request_data))
            # response should return a page
            assert resp.status_code == 200


def test_cases_query(app, case_obj, institute_obj):
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

def test_cases_panel_query(app, case_obj, parsed_panel, institute_obj):
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

def test_institutes(app):
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

def test_case(app, case_obj, institute_obj):
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


def test_case_synopsis(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        req_data = {
            'synopsis' : 'test synopsis'
        }

        # WHEN updating the synopsis of a case
        resp = client.get(url_for('cases.case_synopsis',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name'],
                                  data=req_data ))
        # then it should return a redirected page
        assert resp.status_code == 302


def test_causatives(app, user_obj, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    # There should be no causative variants for test case:
    assert 'causatives' not in case_obj
    var1_id = '4c7d5c70d955875504db72ef8e1abe77' # in POT1 gene
    var2_id = 'e24b65bf27feacec6a81c8e9e19bd5f1' # in TBX1 gene
    var_ids = [var1_id, var2_id]

    # for each variant
    for var_id in var_ids:
        # update case by marking variant as causative:
        variant_obj = store.variant(document_id=var_id)
        store.mark_causative(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link='causative_var_link/{}'.format(variant_obj['_id']),
            variant=variant_obj
        )
    updated_case = store.case_collection.find_one({'_id':case_obj['_id']})
    # The above variants should be registered as causatives in case object
    assert updated_case['causatives'] == var_ids

    # Call scout causatives view and check if the above causatives are displayed
    with app.test_client() as client:

        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.get(url_for('cases.causatives',
                                  institute_id=institute_obj['internal_id']))

        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # and variant 2
        assert var2_id in str(resp.data)

        # Filter causatives by gene (POT1)
        resp = client.get(url_for('cases.causatives',
                                  institute_id=institute_obj['internal_id'],
                                  query='17284 | POT1 (DKFZp586D211, hPot1, POT1)'))
        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # but NOT variant 2
        assert var2_id not in str(resp.data)


def test_case_report(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # When clicking on 'general' button on case page
        resp = client.get(url_for('cases.case_report',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name']),
                                  )
        # a successful response should be returned
        assert resp.status_code == 200


def test_case_diagnosis(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        req_data = {
            'omim_id' : 'OMIM:615349'
        }

        # When updating an OMIM diagnosis for a case
        resp = client.get(url_for('cases.case_diagnosis',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name']),
                                  data=req_data
                                  )
        # Response should be redirected to case page
        assert resp.status_code == 302


def test_pdf_case_report(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # When clicking on 'Download PDF' button on general report page
        resp = client.get(url_for('cases.pdf_case_report',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name']),
                                  )
        # a successful response should be returned
        assert resp.status_code == 200


def test_clinvar_submissions(app, institute_obj):
    # Test the web page containing the clinvar submissions for an institute

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # When visiting the clinvar submissiin page (get request)
        resp = client.get(url_for('cases.clinvar_submissions',
                                  institute_id=institute_obj['internal_id']))

        # a successful response should be returned
        assert resp.status_code == 200


def test_mt_report(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # When clicking on 'mtDNA report' on case page
        resp = client.get(url_for('cases.mt_report',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name']),
                                  )
        # a successful response should be returned
        assert resp.status_code == 200
        # and it should contain a zipped file, not HTML code
        assert resp.mimetype == 'application/zip'


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
        res = store.case_collection.find({'mme_submission':{'$exists' : True}})
        assert sum(1 for i in res) == 1

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
        res = store.case_collection.find({'mme_submission':{'$exists' : True}})
        assert sum(1 for i in res) == 1

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
        res = store.case_collection.find({'mme_submission':{'$exists' : True}})
        assert sum(1 for i in res) == 1

        # WHEN accessing the case page
        resp = client.post(url_for('cases.matchmaker_delete',
                                institute_id=institute_obj['internal_id'],
                                case_name=case_obj['display_name']))
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302


def test_status(app, institute_obj, case_obj, user_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # make sure test case status is inactive
        assert case_obj['status'] == 'inactive'

        # use status view to update status for test case
        request_data = {
            'status' : 'prioritized'
        }
        resp = client.post(url_for('cases.status',
                                institute_id=institute_obj['internal_id'],
                                case_name=case_obj['display_name'], params=request_data))

        assert resp.status_code == 302 # page should be redirected
