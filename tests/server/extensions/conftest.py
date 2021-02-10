"""Fixtures for extenstions"""
import pytest

from scout.server.extensions.loqus_extension import LoqusDB


@pytest.fixture(name="loqus_exe")
def fixture_loqus_exe():
    """Return the path to a loqus executable"""
    return "a/path/to/loqusdb"


@pytest.fixture(name="loqus_version")
def fixture_loqus_version():
    """Return a loqus version"""
    return 2.5


@pytest.fixture(name="loqus_config")
def fixture_loqus_config():
    """Return the path to a loqus config"""
    return "configs/loqus-config.yaml"


@pytest.fixture(name="loqus_api_url")
def fixture_loqus_api_url():
    """Return the url to a loqus REST API instance"""
    return "url/to/loqus/api"


@pytest.fixture(name="loqus_api_extension")
def fixture_loqus_api_extension(loqus_api_url):
    """Return a loqusdb extension"""
    loqus_obj = LoqusDB(api_url=loqus_api_url, version=loqus_version)
    return loqus_obj


@pytest.fixture(name="loqus_exe_extension")
def fixture_loqus_exe_extension(loqus_exe, loqus_config, loqus_version):
    """Return a loqusdb extension"""
    loqus_obj = LoqusDB(
        loqusdb_binary=loqus_exe, loqusdb_config=loqus_config, version=loqus_version
    )
    return loqus_obj
