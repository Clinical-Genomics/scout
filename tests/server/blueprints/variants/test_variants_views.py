# -*- coding: utf-8 -*-
from flask import url_for, current_app
from flask_login import current_user
from urllib.parse import urlencode


def test_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the variants page
        resp = client.get(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_variants_research(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the variants page
        resp = client.get(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_type="research",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # THEN a reset filters link with variant type should have been made
        assert "variant_type=research" in str(resp.data)


def test_variants_post_data(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN submitting form data to the page (POST method)
        data = urlencode({"clinical_filter": True})  # clinical filter

        # WHEN requesting a clinical filter to variants page
        resp = client.post(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
            content_type="application/x-www-form-urlencoded",
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_sv_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the sv-variants page
        resp = client.get(
            url_for(
                "variants.sv_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_sv_variants_research(app, institute_obj, case_obj):
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the sv-variants page
        resp = client.get(
            url_for(
                "variants.sv_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_type="research",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # THEN a reset filters link with variant type should have been made
        assert "variant_type=research" in str(resp.data)


def test_sv_variants_post_data(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN requesting a clinical filter from the page (POST method)
        data = urlencode({"clinical_filter": True})  # clinical filter

        # WHEN posting an update description request to panel page
        resp = client.post(
            url_for(
                "variants.sv_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
            content_type="application/x-www-form-urlencoded",
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_str_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the str-variants page
        resp = client.get(
            url_for(
                "variants.str_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_cancer_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

    # WHEN accessing the sv-variants page
    resp = client.get(
        url_for(
            "variants.cancer_variants",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
        )
    )
    # THEN it should return a page
    assert resp.status_code == 200


def test_sv_cancer_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

    # WHEN accessing the sv-variants page
    resp = client.get(
        url_for(
            "variants.cancer_sv_variants",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
        )
    )
    # THEN it should return a page
    assert resp.status_code == 200
