# -*- coding: utf-8 -*-
from flask import url_for, current_app
from flask_login import current_user
from urllib.parse import urlencode
from scout.server.extensions import store


def test_acmg(app):

    # GIVEN an initialized app
    with app.test_client() as client:

        # the acmg endpoint endpoint should return an acmg json file
        resp = client.get("/api/v1/acmg")
        assert resp.status_code == 200
        assert resp.data


def test_variant(app, institute_obj, case_obj, variant_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the variant page
        resp = client.get(
            url_for(
                "variant.variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_sv_variant(app, institute_obj, case_obj, variant_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the sv_variant page
        resp = client.get(
            url_for(
                "variant.sv_variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_variant_update_manual_rank(app, case_obj, variant_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When a manual Rank is assigned to the variant via POST request
        data = urlencode({"manual_rank": "7"})  # pathogenic
        resp = client.post(
            url_for(
                "variant.variant_update",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
                data=data,
                content_type="application/x-www-form-urlencoded",
            )
        )
        # THEN request should be a redirection
        assert resp.status_code == 302


def test_variant_update_cancer_tier(app, case_obj, variant_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When a cancer tier is assigned to the variant via POST request
        data = urlencode({"cancer_tier": "2C"})  # pathogenic
        resp = client.post(
            url_for(
                "variant.variant_update",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],  # let's assume this is a cancer variant
                data=data,
                content_type="application/x-www-form-urlencoded",
            )
        )
        # THEN request should be a redirection
        assert resp.status_code == 302


def test_clinvar(app, case_obj, variant_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the page is accessed via GET request
        resp = client.get(
            url_for(
                "variant.clinvar",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            )
        )
        # Then it should return a page
        assert resp.status_code == 200

        # WHEN instead the page is requested via POST method
        # using a test clinvar form:
        data = urlencode(
            {
                "main_var": variant_obj["_id"],
                "@".join(["local_id", variant_obj["_id"]]): variant_obj["_id"],
                "@".join(["chromosome", variant_obj["_id"]]): variant_obj["chromosome"],
                "@".join(["start", variant_obj["_id"]]): variant_obj["position"],
                "@".join(["stop", variant_obj["_id"]]): variant_obj["end"],
                "@".join(["condition_id_value", variant_obj["_id"]]): [
                    "HPO_HP:0001250",
                    "OMIM_145590",
                ],
                "@".join(["clin_features", variant_obj["_id"]]): ["HPO_HP:0001507"],
            }
        )
        resp = client.post(
            url_for(
                "variant.clinvar",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            ),
            data=data,
            content_type="application/x-www-form-urlencoded",
        )
        # THEN the request status should be a redirect
        assert resp.status_code == 302
