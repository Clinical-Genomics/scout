# -*- coding: utf-8 -*-
from flask import url_for, current_app
from flask_login import current_user
from urllib.parse import urlencode

def test_variant(app, institute_obj, case_obj, variant_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the variant page
        resp = client.get(url_for('variant.variant',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name'],
                                  variant_id=variant_obj['_id']
                                  ))
        # THEN it should return a page
        assert resp.status_code == 200

def test_sv_variant(app, institute_obj, case_obj, variant_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the sv_variant page
        resp = client.get(url_for('variant.sv_variant',
                                  institute_id=institute_obj['internal_id'],
                                  case_name=case_obj['display_name'],
                                  variant_id=variant_obj['_id']
                                  ))
        # THEN it should return a page
        assert resp.status_code == 200
