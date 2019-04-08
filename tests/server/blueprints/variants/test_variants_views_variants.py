# -*- coding: utf-8 -*-
from flask import url_for

def test_server_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the phenotypes page
        resp = client.get(url_for('variants.variants',
            institute_id=institute_obj['internal_id'],
            case_name=case_obj['display_name']))

        # THEN it should return a page
        assert resp.status_code == 200
