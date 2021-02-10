"""Fixtures for extenstions"""
import pytest
from scout.server.app import create_app


@pytest.fixture(name="loqus_exe")
def fixture_loqus_exe():
    """Return the path to a loqus executable"""
    return "a/path/to/loqusdb"


@pytest.fixture(name="loqus_config")
def fixture_loqus_config():
    """Return the path to a loqus config"""
    return "configs/loqus-config.yaml"


@pytest.fixture(name="loqus_exe_app")
def ffixture_loqus_exe_app(loqus_exe, loqus_config):
    """Return an connected to LoqusDB via Loqus executable"""

    app = create_app(
        config=dict(
            TESTING=True,
            LOQUSDB_SETTINGS={"loqusdb_binary": loqus_exe, "loqusdb_config": loqus_config},
        )
    )
    return app


@pytest.fixture(name="loqus_api_app")
def fixture_loqus_api_app():
    """Return an connected to LoqusDB via REST API"""

    app = create_app(
        config=dict(
            TESTING=True,
            LOQUSDB_SETTINGS={"api_url": "url/to/loqus/api"},
        )
    )
    return app
