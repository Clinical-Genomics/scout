"""Tests for the Case Rerunner extension"""

from scout.server.extensions import rerunner


def test_rerunner_connection_settings(rerunner_app):
    """Test that the app is initialized with the Rerunner settings"""

    host = "test_rerunner_url"
    port = 9000
    key = "test_key"

    assert rerunner.connection_settings["host"] == f"{host}:{port}"
    assert rerunner.connection_settings["api_key"] == key
