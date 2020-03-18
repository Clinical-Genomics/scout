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


@pytest.fixture(name="app_config")
def fixture_app_config(loqus_exe, loqus_config, loqus_version):
    """Return a dictionary with loqus configs"""
    _configs = {
        "LOQUSDB_SETTINGS": {
            "binary_path": loqus_exe,
            "version": loqus_version,
            "config_path": loqus_config,
        }
    }

    return _configs


@pytest.fixture(name="loqus_extension")
def fixture_loqus_extension(loqus_exe, loqus_config, loqus_version):
    """Return a loqusdb extension"""
    loqus_obj = LoqusDB(
        loqusdb_binary=loqus_exe, loqusdb_config=loqus_config, version=loqus_version
    )
    return loqus_obj
