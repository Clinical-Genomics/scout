# -*- coding: utf-8 -*-
from flask import url_for

from scout.server.extensions import store


def test_managed_variants(app, user_obj, institute_obj):
    """Test managed variants view"""
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the managed variants page
        resp = client.get(url_for("managed_variants.managed_variants"))

        # THEN it should return a page
        assert resp.status_code == 200


def test_add_and_remove_managed_variants(app, user_obj, institute_obj, mocker, mock_redirect):
    """Test first managed variants views:
    adding a managed variant,
    trying to add it again in duplicate and finally removing it.
    """
    mocker.patch(
        "scout.server.blueprints.managed_variants.views.redirect", return_value=mock_redirect
    )
    # GIVEN an initialized app
    # GIVEN a user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # GIVEN data from a filled out form
        add_form_data = {
            "chromosome": "14",
            "position": 76548781,
            "end": 76548781,
            "category": "snv",
            "sub_category": "indel",
            "reference": "CTGGACC",
            "alternative": "G",
        }

        # WHEN attempting to add a valid variant
        resp = client.post(
            url_for("managed_variants.add_managed_variant"),
            data=add_form_data,
        )
        # THEN status should be redirect
        assert resp.status_code == 302
        # THEN one variant should be present in the managed variant collection
        assert sum(1 for i in store.managed_variant_collection.find()) == 1
        # THEN the correct variant should be found inserted into the database
        test_managed_variant = store.managed_variant_collection.find_one()
        assert test_managed_variant["chromosome"] == "14"

        # THEN attempting a duplicate insertion will return an error
        resp = client.post(url_for("managed_variants.add_managed_variant"), data=add_form_data)
        # THEN the status code should still be redirect
        assert resp.status_code == 302
        # THEN the database should still contatain only one variant
        assert sum(1 for i in store.managed_variant_collection.find()) == 1

        # WHEN requesting to remove the selected variant
        resp = client.post(
            url_for(
                "managed_variants.remove_managed_variant",
                variant_id=test_managed_variant["managed_variant_id"],
            )
        )
        # THEN the status code should again be redirect
        assert resp.status_code == 302
        # THEN no variants should remain in the collection
        assert sum(1 for i in store.managed_variant_collection.find()) == 0
