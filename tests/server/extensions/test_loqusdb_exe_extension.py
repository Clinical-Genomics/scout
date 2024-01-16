"""Tests for the loqusdb executable extension"""

import subprocess

import pytest

from scout.exceptions.config import ConfigError
from scout.server.app import create_app
from scout.server.extensions import LoqusDB, loqus_extension, loqusdb


def test_set_coordinates_no_variant_type():
    """Test update coordinates when nothing to update"""
    # GIVEN a variant with some coordinates
    pos = 10
    end = 10
    length = 1
    var = {
        "_id": "1_10_A_C",
        "pos": pos,
        "end": end,
        "length": length,
    }
    # WHEN setting the coordinates
    LoqusDB.set_coordinates(var)
    # THEN assert that nothing changed
    assert var["pos"] == pos
    assert var["end"] == end
    assert var["length"] == length


def test_set_coordinates_ins():
    """Test update coordinates when hidden insertion"""
    # GIVEN a variant with some coordinates
    pos = 10
    end = 10
    length = 10
    var_type = "INS"
    var = {
        "_id": "1_10_INS",
        "pos": pos,
        "end": end,
        "length": length,
        "variant_type": var_type,
    }
    # WHEN setting the coordinates
    LoqusDB.set_coordinates(var)
    # THEN assert that end coordinate is updated
    assert var["pos"] == pos
    assert var["end"] == end + length
    assert var["length"] == length


def test_set_coordinates_unknown_ins():
    """Test update coordinates when insertion length is unknown"""
    # GIVEN a variant with some coordinates
    pos = 10
    end = 10
    length = -1
    var_type = "INS"
    var = {
        "_id": "1_10_INS",
        "pos": pos,
        "end": end,
        "length": length,
        "variant_type": var_type,
    }
    # WHEN setting the coordinates
    LoqusDB.set_coordinates(var)
    # THEN assert that end coordinate is updated
    assert var["pos"] == pos
    assert var["end"] == end
    assert var["length"] == length


def test_get_bin_path_wrong_instance(loqus_exe_app):
    """Test get_bin_path when the instance is not available"""

    # When the get_bin_path function is invoked for a non-existing loqus instance
    with loqus_exe_app.app_context():
        # THEN it should raise ConfigError
        with pytest.raises(ConfigError):
            assert loqusdb.get_bin_path(loqusdb_id="FOO")


def test_get_config_path_wrong_instance(loqus_exe_app):
    """Test get_config_path when the instance is not available"""

    # When the get_config_path function is invoked for a non-existing loqus instance
    with loqus_exe_app.app_context():
        # THEN it should raise ConfigError
        with pytest.raises(ConfigError):
            assert loqusdb.get_config_path(loqusdb_id="FOO")


def test_get_exec_loqus_version_CalledProcessError(loqus_exe_app, monkeypatch):
    """Test the error triggered when retrieving the version of a LoqusDB instance not properly configured"""

    # GIVEN a mocked subprocess that gives error
    def mocksubprocess(*args, **kwargs):
        raise subprocess.CalledProcessError(None, None)

    monkeypatch.setattr(subprocess, "check_output", mocksubprocess)

    # When the get_exec_loqus_version function is invoked
    with loqus_exe_app.app_context():
        # It will trigger the same error and return -1
        assert loqusdb.get_exec_loqus_version("default") == "-1.0"


def test_loqusdb_exe_variant(loqus_exe_app, monkeypatch, loqus_exe_variant):
    """Test to fetch a variant from loqusdb executable instance"""

    # GIVEN a mocked subprocess command
    def mockcommand(*args):
        return loqus_exe_variant

    monkeypatch.setattr(loqus_extension, "execute_command", mockcommand)

    with loqus_exe_app.app_context():
        # WHEN fetching the variant info
        var_info = loqusdb.get_variant({"_id": "a variant"})
        # THEN assert the info was parsed correct
        assert var_info["total"] == 3


def test_loqusdb_exe_variant_CalledProcessError(loqus_exe_app, monkeypatch):
    """Test fetching a variant from loqusdb executable that raises an exception"""

    # GIVEN replacing subprocess.check_output to raise CalledProcessError
    def mockcommand(*args):
        raise subprocess.CalledProcessError(123, "case_count")

    monkeypatch.setattr(loqus_extension, "execute_command", mockcommand)

    with loqus_exe_app.app_context():
        # THEN raised exception is caught and an empty dict is returned
        assert {} == loqusdb.get_variant({"_id": "a variant"})


def test_init_app_loqus_list(monkeypatch, loqus_exe, loqus_config):
    """Test creating a Loqus extension from a list of config params"""

    # GIVEN a mocked loqus exe instance returning a supported loqus version
    def mockcommand(*args):
        return "2.5"

    monkeypatch.setattr(loqus_extension, "execute_command", mockcommand)

    # The app shold be created by providing LoqusDB params as a list
    app = create_app(
        config=dict(LOQUSDB_SETTINGS=[{"binary_path": loqus_exe, "loqusdb_config": loqus_config}])
    )
    assert app


def test_init_app_loqus_dict(monkeypatch, loqus_exe, loqus_config):
    """Test creating a Loqus extension from dictionary settings"""

    # GIVEN a mocked loqus exe instance returning a supported loqus version
    def mockcommand(*args):
        return "2.5"

    monkeypatch.setattr(loqus_extension, "execute_command", mockcommand)

    # The app shold be created by providing LoqusDB params as a dictionary
    app = create_app(
        config=dict(
            LOQUSDB_SETTINGS={
                "id": "default",
                "binary_path": loqus_exe,
                "loqusdb_config": loqus_config,
            }
        )
    )
    assert app


def test_loqusdb_settings_list_to_dict():
    """Test handling of deprecated settings: list of settings becomes a dictionary with instance ids as keys"""
    cfg_1 = {"id": "default", "binary_path": "test_binary"}
    cfg_2 = {"id": "test_exe", "api_url": "test_url"}
    list_cfg = [cfg_1, cfg_2]

    # GIVEN a LoqusDB extensions instantiated with deprecated param (list)
    loqusdb.settings_list_to_dict(list_cfg)

    # The instance should have settings as dict, with as many key/values as the elements of the initial list
    assert len(loqusdb.loqusdb_settings.keys()) == 2
    assert cfg_1["id"] in loqusdb.loqusdb_settings
    assert cfg_2["id"] in loqusdb.loqusdb_settings
