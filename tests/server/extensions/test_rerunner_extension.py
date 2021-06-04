"""Tests for the Case Rerunner extension"""
from scout.server.extensions import rerunner


def test_rerunner_connection_settings(rerunner_app):
    """Test that the app is initialized with the Rerunner settings"""

    assert rerunner.connection_settings["entrypoint"]
    assert rerunner.connection_settings["api_key"]
