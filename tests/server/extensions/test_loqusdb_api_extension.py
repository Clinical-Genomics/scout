"""Tests for the loqusdb REST API extension"""

from scout.server.extensions import loqusdb, loqus_extension


def test_loqusdb_api_settings(loqus_api_app):
    """test that the app is initialized with the correct Loqus API settings"""

    with loqus_api_app.app_context():
        assert "default" in loqusdb.__dict__["loqus_ids"]
        assert isinstance(loqusdb.__dict__.get("loqusdb_settings"), list)


def test_loqusdb_api_variant(loqus_api_app, monkeypatch, loqus_api_variant):
    """Test to fetch a variant from loqusdb executable instance"""

    # GIVEN a mocked loqus API
    def mockapi(*args):
        return loqus_api_variant

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the variant info
        var_info = loqusdb.get_variant({"_id": "a variant", "category": "snv"})
        # THEN assert the info was parsed correct

        assert var_info["observations"] == loqus_api_variant["observations"]
        assert var_info["families"] == loqus_api_variant["families"]
