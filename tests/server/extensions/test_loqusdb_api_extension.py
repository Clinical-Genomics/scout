"""Tests for the loqusdb REST API extension"""

from scout.server.extensions import loqus_extension, loqusdb


def test_loqusdb_api_settings(loqus_api_app):
    """Test that the app is initialized with the correct Loqus API settings"""

    with loqus_api_app.app_context():
        assert "default" in loqusdb.__dict__["loqus_ids"]
        assert isinstance(loqusdb.loqusdb_settings, dict)


def test_get_api_loqus_version_no_connection(loqus_api_app):
    """Test function that returns the version of the LoqusDB API when the API is not available"""

    # When the get_api_loqus_version function is invoked for a non-reachable API
    # THEN it should set the loqus version to None
    with loqus_api_app.app_context():
        assert loqusdb.get_api_loqus_version(api_url="test_url") == None


def test_get_api_loqus_version(loqus_api_app, monkeypatch):
    """Test function that returns the version of the LoqusDB API instance"""

    # GIVEN a mocked loqus API
    def mockapi(*args):
        return {
            "content": {
                "message": "Welcome to the loqusdbapi",
                "loqusdb_version": "2.5",
            },
            "status_code": 200,
        }

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the Loqus version
        version = loqusdb.get_instance_version(loqusdb.loqusdb_settings["default"])

        # THEN the returned version should be a double
        assert version == "2.5"


def test_loqus_api_variant_no_instance(loqus_api_app):
    """Test fetching info on a variant from loqusdb API when the instance is not available"""

    with loqus_api_app.app_context():
        # WHEN fetching the variant info
        var_info = loqusdb.get_variant(
            {"_id": "a variant", "category": "snv"}, "non_valid_instance"
        )

        # THEN the API info should return None
        assert var_info is None


def test_loqusdb_api_snv_variant(loqus_api_app, monkeypatch, loqus_api_variant):
    """Test fetching a SNV variant info from loqusdb API"""

    # GIVEN a mocked loqus API
    def mockapi(*args):
        return {"content": loqus_api_variant, "status_code": 200}

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the variant info
        var_info = loqusdb.get_variant({"_id": "a variant", "category": "snv"})

        # THEN assert the info was retrieved correctly
        assert var_info["observations"] == loqus_api_variant["observations"]


def test_loqus_api_snv_variant_not_found(loqus_api_app, monkeypatch, loqus_api_variant):
    # GIVEN a mocked loqus API that doesn't return usable info
    def mockapi(*args):
        return {"content": {"detail": "Not Found"}, "status_code": 404}

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the variant info
        var_info = loqusdb.get_variant({"_id": "a variant", "category": "snv"})

        # THEN the loqusdb extensions should return an empty dictionary
        assert var_info == {}


def test_loqusdb_api_sv_variant(loqus_api_app, monkeypatch, loqus_api_variant):
    """Test fetching a SV variant info from loqusdb API"""

    # GIVEN a mocked loqus API
    def mockapi(*args):
        return {"content": loqus_api_variant, "status_code": 200}

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the SV variant info
        var_info = loqusdb.get_variant(
            {
                "chrom": "1",
                "end_chrom": "1",
                "pos": 7889972,
                "end": 7889995,
                "variant_type": "DUP",
                "category": "sv",
            }
        )

        # THEN assert the info was retrieved correctly
        assert var_info["observations"] == loqus_api_variant["observations"]
