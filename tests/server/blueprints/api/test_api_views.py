from flask import url_for


def test_case(app, case_obj):
    """Test the API that returns a case as a json object"""

    case_name = case_obj["display_name"]

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))
        # WHEN the API is invoked with the right params
        resp = client.get(
            url_for(
                "api.case",
                institute_id=case_obj["owner"],
                case_name=case_name,
            )
        )
        # THEN it should return a valid response
        assert resp.status_code == 200
        assert resp.json["display_name"] == case_name


def test_variant(app, case_obj, variant_obj):
    """Test the API that returns a variant as a json object"""

    case_name = case_obj["display_name"]
    variant_id = variant_obj["_id"]

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))
        # WHEN the API is invoked with the right params
        resp = client.get(
            url_for(
                "api.variant",
                variant_id=variant_id,
                institute_id=case_obj["owner"],
                case_name=case_name,
            )
        )
        # THEN it should return a valid response
        assert resp.status_code == 200
        assert resp.json["_id"] == variant_id


def test_pin(app, case_obj, variant_obj):
    """Test the api endpoint that pins variants"""

    case_name = case_obj["display_name"]
    variant_id = variant_obj["_id"]

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # WHEN the API is invoked with the right params
        resp = client.get(
            url_for(
                "api.pin_variant",
                variant_id=variant_id,
                institute_id=case_obj["owner"],
                case_name=case_name,
                link="pinned it",
            )
        )
        # THEN it should return a valid response
        assert resp.status_code == 200
        assert resp.json["_id"] == variant_id


def test_unpin(app, institute_obj, case_obj, variant_obj):
    """Test the api endpoint that unpins variants"""

    case_name = case_obj["display_name"]
    variant_id = variant_obj["_id"]

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN a pinned variant
        resp = client.get(
            url_for(
                "api.pin_variant",
                institute_id=case_obj["owner"],
                case_name=case_name,
                variant_id=variant_id,
                link="pinned it for testing",
            )
        )
        assert resp.status_code == 200

        # WHEN the API is invoked with the right params
        resp = client.get(
            url_for(
                "api.unpin_variant",
                variant_id=variant_id,
                institute_id=case_obj["owner"],
                case_name=case_name,
                link="unpinned it",
            )
        )
        # THEN it should return a valid response
        assert resp.status_code == 200
        assert resp.json["_id"] == variant_id
