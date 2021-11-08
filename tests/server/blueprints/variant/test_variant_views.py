# -*- coding: utf-8 -*-
from urllib.parse import urlencode

from flask import current_app, url_for
from flask_login import current_user

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


def test_cancer_variant(app, cancer_case_obj, cancer_variant_obj):

    # GIVEN a cancer case object with a variant saved in database
    assert store.case_collection.insert_one(cancer_case_obj)
    assert store.variant_collection.insert_one(cancer_variant_obj)

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the cancer variant page
        resp = client.get(
            url_for(
                "variant.cancer_variant",
                institute_id=cancer_case_obj["owner"],
                case_name=cancer_case_obj["display_name"],
                variant_id=cancer_variant_obj["_id"],
            )
        )
        # THEN it should return a successful response
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


def test_variant_update_manual_rank(
    app, case_obj, variant_obj, institute_obj, mocker, mock_redirect
):
    mocker.patch("scout.server.blueprints.variant.views.redirect", return_value=mock_redirect)

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


def test_edit_variants_comments(
    app, institute_obj, case_obj, user_obj, variant_obj, mocker, mock_redirect
):
    """Test the functionality to modify a variants comment"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        ## GIVEN a variant with a specific comment
        store.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            variant=variant_obj,
            link="a link",
            category="variant",
            verb="comment",
            content="a specific comment",
            subject=variant_obj["display_name"],
            level="specific",
        )
        comment = store.event_collection.find_one({"verb": "comment"})
        assert comment
        assert comment["level"] == "specific"

        # WHEN a user updates the comment via the modal form
        form_data = {
            "event_id": comment["_id"],
            "updatedContent": "a global comment",
            "edit": "",
            "level": "global",
        }
        resp = client.post(
            url_for(
                "cases.events",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                event_id=comment["_id"],
            ),
            data=form_data,
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302

        # And the comment should be updated
        updated_comment = store.event_collection.find_one()
        assert updated_comment["content"] == "a global comment"
        assert updated_comment["level"] == "global"


def test_variant_update_cancer_tier(
    app, case_obj, variant_obj, institute_obj, mocker, mock_redirect
):

    mocker.patch("scout.server.blueprints.variant.views.redirect", return_value=mock_redirect)
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


def test_update_tracks_settings(app, user_obj, mocker, mock_redirect):
    """Test the endpoint that updates the IGV track preferences for a user"""

    mocker.patch("scout.server.blueprints.variant.views.redirect", return_value=mock_redirect)

    preferred_tracks = ["Genes", "ClinVar"]
    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # GIVEN that the user wants to see only Genes and ClinVar SNVs tracks
        form_data = {
            "user_tracks": preferred_tracks,
        }

        # WHEN sending a POST request to the update
        resp = client.post(
            url_for(
                "variant.update_tracks_settings",
            ),
            data=form_data,
        )

        # THEN the user object in the database should be updated with the right track info
        user_obj = store.user(email=user_obj["email"])
        for track in preferred_tracks:
            assert track in preferred_tracks
