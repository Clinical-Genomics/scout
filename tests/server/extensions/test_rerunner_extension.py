"""Tests for the Case Rerunner extension"""

from scout.server.app import create_app
from scout.server.extensions import rerunner


def test_rerunner_connection_settings():
    """Test that the app is initialized with the Rerunner settings"""

    host = "test_rerunner_url"
    port = 9000
    timeout = 10
    key = "test_key"

    # WHEN app is created
    test_app = create_app(
        config=dict(
            TESTING=True,
            RERUNNER_HOST=host,
            RERUNNER_PORT=port,
            RERUNNER_TIMEOUT=timeout,
            RERUNNER_API_KEY=key,
        )
    )

    assert rerunner.connection_settings["host"] == f"{host}:{port}"
    assert rerunner.connection_settings["api_key"] == key
