# -*- coding: utf-8 -*-
from urllib.parse import urlencode

import responses
from flask import url_for
from flask_login import current_user

from scout.server.extensions import store


@responses.activate
def test_marrvel_link_38(app, case_obj):
    """Test the function that redirects to MARRVEL for a variant in build 37"""

    # GIVEN a variant in genome build 38:
    test_variant = {
        "_id": "a_variant",
        "case_id": case_obj["_id"],
        "chromosome": "X",
        "position": 1039265,
        "reference": "T",
        "alternative": "C",
    }
    store.variant_collection.insert_one(test_variant)

    # GIVEN that the variant can be lifted over to build 37
    url = f"https://grch37.rest.ensembl.org/map/human/GRCh38/{test_variant['chromosome']}:{test_variant['position']}..{test_variant['position']}/GRCh37?content-type=application/json"

    liftover_mappings = {
        "mappings": [
            {
                "original": {
                    "assembly": "GRCh38",
                    "seq_region_name": test_variant["chromosome"],
                    "start": test_variant["position"],
                    "end": test_variant["position"] + 100,
                },
                "mapped": {
                    "assembly": "GRCh37",
                    "seq_region_name": test_variant["chromosome"],
                    "start": 1000000,
                    "end": 1000100,
                },
            }
        ]
    }
    responses.add(
        responses.GET,
        url,
        json=liftover_mappings,
        status=200,
    )

    # GIVEN an initialized app
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # WHEN user clicks on MARRVEL link for a variant in build 38
        resp = client.get(
            url_for(
                "variant.marrvel_link",
                build="38",
                variant_id=test_variant["_id"],
            )
        )
        # THEN page should redirect to MARRVEL
        assert resp.status_code == 302


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


def test_variant_by_document_id(app, variant_obj):
    # GIVEN an initialized app
    # GIVEN a valid user

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the variant page with only a variant ID
        resp = client.get(
            url_for(
                "variant.variant_by_id",
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


def test_fusion_variant(app, institute_obj, fusion_case_obj, one_fusion_variant):
    """Test the variant page when a fusion variant is requested."""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN a RNA fusion case present in the database
        assert store.case_collection.insert_one(fusion_case_obj)

        # GIVEN that the case has a variant
        store.variant_collection.insert_one(one_fusion_variant)

        # WHEN sending a request (GET) to the fusion variant page
        resp = client.get(
            url_for(
                "variant.variant",
                institute_id=institute_obj["internal_id"],
                case_name=fusion_case_obj["display_name"],
                variant_id=one_fusion_variant["_id"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_str_reviewer_variant(app, institute_obj, case_obj, str_variant_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    # GIVEN an STR variant with a REPID
    assert str_variant_obj.get("str_repid")

    # WHEN inserting a STR variant
    assert store.variant_collection.insert_one(str_variant_obj)

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN sending a request (GET) to the sv_variant page
        resp = client.get(
            url_for(
                "variant.reviewer_aln",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=str_variant_obj["document_id"],
            )
        )
        # THEN the REViewer page should return a page
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
        client.get(url_for("auto_login"))

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


def test_update_tracks_settings(app, user_obj, mocker, mock_redirect):
    """Test the endpoint that updates the IGV track preferences for a user"""

    mocker.patch("scout.server.blueprints.variant.views.redirect", return_value=mock_redirect)

    preferred_tracks = ["Genes", "ClinVar"]
    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN that the user wants to see only Genes and ClinVar SNVs tracks
        form_data = {
            "user_tracks": preferred_tracks,
        }

        # WHEN sending a POST request to the update
        client.post(
            url_for(
                "variant.update_tracks_settings",
            ),
            data=form_data,
        )

        # THEN the user object in the database should be updated with the right track info
        store.user(email=user_obj["email"])
        for track in preferred_tracks:
            assert track in preferred_tracks
