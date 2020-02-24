# -*- coding: utf-8 -*-
from flask import url_for

def test_case_api(app, case_obj, institute_obj):
    """Test the case API that returns a case json object"""

    # GIVEN an initialized app
    # GIVEN a valid user, case and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case API page
        resp = client.get(
            url_for(
                "api.case",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"]
            )
        )
        # THEN the response should contain case data
        data_string = resp.data.decode('utf-8')
        assert case_obj["display_name"] in data_string


def test_variant_api(app, case_obj, institute_obj, variant_obj):
    """Test the case API that returns a variant json object"""

    # GIVEN an initialized app
    # GIVEN a valid user, case and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the variant API page
        resp = client.get(
            url_for(
                "api.variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"]
            )
        )
        # THEN the response should contain variant data
        data_string = resp.data.decode('utf-8')
        assert variant_obj["display_name"] in data_string
