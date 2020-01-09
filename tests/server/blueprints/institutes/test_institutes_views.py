# -*- coding: utf-8 -*-
from flask import url_for
from scout.server.extensions import store

def test_overview(app, user_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for('overview.institutes'))

        # THEN it should return a page
        assert resp.status_code == 200


def test_institute(app, user_obj, institute_obj):
    """Test function that creates institute update form"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:

        client.get(url_for('auto_login'))

        # WHEN accessing the cases page (GET method)
        resp = client.get(url_for('overview.institute', institute_id=institute_obj['internal_id']))

        # THEN it should return a page
        assert resp.status_code == 200

        # WHEN trying to edit institute object from the same pag
        assert institute_obj['display_name'] == 'test_institute'
        assert institute_obj['sanger_recipients'] == ['john@doe.com', 'jane@doe.com']
        assert institute_obj.get('phenotype_groups') is None
        assert institute_obj['coverage_cutoff'] == 10
        assert institute_obj['frequency_cutoff'] == 0.01
        assert institute_obj.get('collaborators') is None

        form_data = {
            'display_name' : 'updated name'
        }

        # by sending a POST request
        resp = client.post( url_for('overview.institute', institute_id=institute_obj['internal_id']),
            data = form_data)

        updated_institute = store.institute_collection.find_one()
        assert updated_institute['display_name'] == 'updated name'
