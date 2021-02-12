"""Tests for the loqusdb REST API extension"""

from scout.server.extensions import loqusdb, loqus_extension


def test_loqusdb_api_settings(loqus_api_app):
    """test that the app is initialized with the correct Loqus API settings"""

    with loqus_api_app.app_context():
        assert "default" in loqusdb.__dict__["loqus_ids"]
        assert isinstance(loqusdb.__dict__.get("loqusdb_settings"), list)


def test_loqusdb_api_snv_variant(loqus_api_app, monkeypatch, loqus_api_variant):
    """Test fetching a SNV variant info from loqusdb API"""

    # GIVEN a mocked loqus API
    def mockapi(*args):
        return loqus_api_variant

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the variant info
        var_info = loqusdb.get_variant({"_id": "a variant", "category": "snv"})

        # THEN assert the info was retrieved correctly
        assert var_info["observations"] == loqus_api_variant["observations"]


def test_loqusdb_api_sn_variant(loqus_api_app, monkeypatch, loqus_api_variant):
    """Test fetching a SV variant info from loqusdb API"""

    # GIVEN a mocked loqus API
    def mockapi(*args):
        return loqus_api_variant

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


def test_loqusdb_api_cases(loqus_api_app, monkeypatch):
    """Test fetching info on number of cases from loqusdb API"""
    nr_snvs = 15
    nr_svs = 12
    # GIVEN a mocked loqus API
    def mockapi(*args):
        return {"nr_cases_snvs": nr_snvs, "nr_cases_svs": nr_svs, "status_code": 200}

    monkeypatch.setattr(loqus_extension, "api_get", mockapi)

    with loqus_api_app.app_context():
        # WHEN fetching the nr_cases with SNV variants
        n_cases = loqusdb.case_count("snv", "default")
        # THEN the API should parse the returned info correctly
        assert n_cases == nr_snvs
