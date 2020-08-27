"""Tests for loqusdb extension"""
import subprocess
from subprocess import CalledProcessError
import pytest
from flask import Flask

from scout.exceptions.config import ConfigError
from scout.server.extensions.loqus_extension import LoqusDB


def test_init_loqusextension(loqus_exe):
    """Test a init a loqus extension object"""
    # GIVEN a loqusdb binary
    # WHEN initialising a loqusdb extension
    loqus_obj = LoqusDB(loqusdb_binary=loqus_exe)
    # THEN assert that the binary is correct
    assert loqus_obj.get_bin_path() == loqus_exe
    # THEN assert that the version is 0
    assert loqus_obj.version is None
    # THEN assert that there is no config
    assert loqus_obj.get_config_path() is None


def test_init_loqusextension_version(loqus_exe, loqus_version):
    """Test a init a loqus extension object with a specified version"""
    # GIVEN a loqusdb binary and a version
    # WHEN initialising a loqusdb extension
    loqus_obj = LoqusDB(loqusdb_binary=loqus_exe, version=loqus_version)
    # THEN assert that the binary is correct
    assert loqus_obj.get_bin_path() == loqus_exe
    # THEN assert that the version is correct
    assert loqus_obj.version == loqus_version
    # THEN assert that there is no config
    assert loqus_obj.get_config_path() is None


def test_init_loqusextension_config(loqus_exe, loqus_config, loqus_version):
    """Test a init a loqus extension object with a specified version"""
    # GIVEN a loqusdb binary, a version and a config
    # WHEN initialising a loqusdb extension
    loqus_obj = LoqusDB(
        loqusdb_binary=loqus_exe, loqusdb_config=loqus_config, version=loqus_version
    )
    # THEN assert that the binary is correct
    assert loqus_obj.get_bin_path() == loqus_exe
    # THEN assert that the version is correct
    assert loqus_obj.version == loqus_version
    # THEN assert that there is no config
    assert loqus_obj.loqusdb_settings == [
        {"id": "default", "binary_path": loqus_exe, "config_path": None}
    ]


def test_init_loqusextension_init_app(loqus_exe, loqus_version):
    """Test a init a loqus extension object with flask app with version"""
    # GIVEN a loqusdb binary
    configs = {"LOQUSDB_SETTINGS": {"binary_path": loqus_exe, "version": loqus_version}}
    # WHEN initialising a loqusdb extension with init app
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with app.app_context():
        app.config = configs
        loqus_obj.init_app(app)
        # THEN assert that the binary is correct
        assert loqus_obj.get_bin_path() == loqus_exe
        # THEN assert that the version is correct
        assert loqus_obj.version == loqus_version
        # THEN assert that config.py has been read
        assert loqus_obj.loqusdb_settings is not None


def test_init_loqusextension_init_app_no_version(mocker, loqus_exe, loqus_version):
    """Test a init a loqus extension object with flask app"""
    # GIVEN a loqusdb binary
    configs = {"LOQUSDB_SETTINGS": {"binary_path": loqus_exe}}
    mocker.patch.object(subprocess, "check_output")
    subprocess.check_output.return_value = b"loqusdb, version %f" % loqus_version
    # WHEN initialising a loqusdb extension with init app
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with app.app_context():
        app.config = configs
        loqus_obj.init_app(app)
        # THEN assert that the binary is correct
        assert loqus_obj.get_bin_path() == loqus_exe
        assert loqus_obj.version == loqus_version
        # THEN assert that there is no config
        # THEN assert that config.py has been read
        assert loqus_obj.loqusdb_settings is not None


def test_init_loqusextension_init_app_wrong_version(loqus_exe):
    """Test a init a loqus extension object with flask app"""
    # GIVEN a loqusdb binary
    configs = {"LOQUSDB_SETTINGS": {"binary_path": loqus_exe, "version": 1.0}}
    # WHEN initialising a loqusdb extension with init app
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with pytest.raises(EnvironmentError):
        with app.app_context():
            app.config = configs
            loqus_obj.init_app(app)


def test_init_loqusextension_init_app_with_config(loqus_exe, loqus_config):
    """Test a init a loqus extension object with flask app with version and config"""
    # GIVEN a loqusdb config as dict
    version = 2.5
    configs = {
        "LOQUSDB_SETTINGS": {
            "binary_path": loqus_exe,
            "version": version,
            "config_path": loqus_config,
        }
    }
    # WHEN initialising a loqusdb extension with init app
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with app.app_context():
        app.config = configs
        loqus_obj.init_app(app)
        # THEN assert that the binary is correct
        assert loqus_obj.get_bin_path() == loqus_exe
        # THEN assert that the version is correct
        assert loqus_obj.version == version
        # THEN assert that the config is correct
        assert loqus_obj.get_config_path() == loqus_config


def test_init_loqusextension_init_app_with_config_multiple(loqus_exe, loqus_config):
    """Test a init a loqus extension object with flask app with version and config"""
    # GIVEN a loqusdb config as list
    version = 2.5
    configs = {
        "LOQUSDB_SETTINGS": [
            {
                "binary_path": loqus_exe,
                "version": version,
                "id": "default",
                "config_path": loqus_config,
            }
        ]
    }

    # WHEN initialising a loqusdb extension with init app
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with app.app_context():
        app.config = configs
        loqus_obj.init_app(app)

        # THEN assert that the binary is correct -with id
        assert loqus_obj.get_bin_path("default") == loqus_exe
        # THEN assert that the binary is correct -without id
        assert loqus_obj.get_bin_path(None) == loqus_exe
        # THEN non-configured id raises
        with pytest.raises(ConfigError):
            assert loqus_obj.get_bin_path("not configured id")

        # THEN assert that the config_path is correct -with id
        assert loqus_obj.get_config_path("default") == loqus_config
        # THEN assert that the config_path is correct -without id
        assert loqus_obj.get_config_path(None) == loqus_config
        # THEN non-configured id raises
        with pytest.raises(ConfigError):
            assert loqus_obj.get_config_path("not configured id")

        # THEN assert that the version is correct -with id
        assert loqus_obj.get_configured_version("default") == version
        # THEN assert that the version is correct -without id
        assert loqus_obj.get_configured_version(None) == version
        # THEN non-configured id raises
        with pytest.raises(ConfigError):
            assert loqus_obj.get_configured_version("not configured id")

        # THEN assert that the version is correct
        assert loqus_obj.version == version
        # THEN assert that the config is correct


def test_init_loqusextension_init_app_get_version(loqus_exe, loqus_version):
    """Test a init a loqus extension object with flask app with version and config"""
    # GIVEN a loqusdb binary

    # THEN initialising a loqusdb extension with init app
    loqus_obj = LoqusDB(version=loqus_version)
    assert loqus_obj.get_version() == loqus_version


def test_init_loqusextension_init_app_get_version_CalledProcessError(
    loqus_exe, loqus_config, mocker
):
    """Test a init a loqus extension object with flask app with version and config"""
    # GIVEN mocking subprocess to raise CalledProcessError
    mocker.patch.object(
        subprocess, "check_output", side_effect=CalledProcessError(123, "case_count")
    )
    configs = {
        "LOQUSDB_SETTINGS": [
            {
                "binary_path": loqus_exe,
                "id": "default",
                "config_path": loqus_config,
            }
        ]
    }
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with app.app_context():
        app.config = configs
        with pytest.raises(EnvironmentError):
            # THEN during app init, version is set to -1 and EnvironmentError is raised
            loqus_obj.init_app(app)
