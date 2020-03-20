"""Tests for loqusdb extension"""
import subprocess

import pytest
from flask import Flask

from scout.server.extensions.loqus_extension import LoqusDB


def test_init_loqusextension(loqus_exe):
    """Test a init a loqus extension object"""
    # GIVEN a loqusdb binary
    # WHEN initialising a loqusdb extension
    loqus_obj = LoqusDB(loqusdb_binary=loqus_exe)
    # THEN assert that the binary is correct
    assert loqus_obj.loqusdb_binary == loqus_exe
    # THEN assert that the base call is correct
    assert loqus_obj.base_call == [loqus_exe]
    # THEN assert that the version is 0
    assert loqus_obj.version == 0
    # THEN assert that there is no config
    assert loqus_obj.loqusdb_config is None


def test_init_loqusextension_version(loqus_exe, loqus_version):
    """Test a init a loqus extension object with a specified version"""
    # GIVEN a loqusdb binary and a version
    # WHEN initialising a loqusdb extension
    loqus_obj = LoqusDB(loqusdb_binary=loqus_exe, version=loqus_version)
    # THEN assert that the binary is correct
    assert loqus_obj.loqusdb_binary == loqus_exe
    # THEN assert that the base call is correct
    assert loqus_obj.base_call == [loqus_exe]
    # THEN assert that the version is correct
    assert loqus_obj.version == loqus_version
    # THEN assert that there is no config
    assert loqus_obj.loqusdb_config is None


def test_init_loqusextension_config(loqus_exe, loqus_config, loqus_version):
    """Test a init a loqus extension object with a specified version"""
    # GIVEN a loqusdb binary, a version and a config
    # WHEN initialising a loqusdb extension
    loqus_obj = LoqusDB(
        loqusdb_binary=loqus_exe, loqusdb_config=loqus_config, version=loqus_version
    )
    # THEN assert that the binary is correct
    assert loqus_obj.loqusdb_binary == loqus_exe
    # THEN assert that the base call is correct
    assert loqus_obj.base_call == [loqus_exe, "--config", loqus_config]
    # THEN assert that the version is correct
    assert loqus_obj.version == loqus_version
    # THEN assert that there is no config
    assert loqus_obj.loqusdb_config == loqus_config


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
        assert loqus_obj.loqusdb_binary == loqus_exe
        # THEN assert that the version is correct
        assert loqus_obj.version == loqus_version
        # THEN assert that there is no config
        assert loqus_obj.loqusdb_config is None


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
        assert loqus_obj.loqusdb_binary == loqus_exe
        assert loqus_obj.version == loqus_version
        # THEN assert that there is no config
        assert loqus_obj.loqusdb_config is None


def test_init_loqusextension_init_app_wrong_version(loqus_exe):
    """Test a init a loqus extension object with flask app"""
    # GIVEN a loqusdb binary
    configs = {"LOQUSDB_SETTINGS": {"binary_path": loqus_exe, "version": 1.0}}
    # WHEN initialising a loqusdb extension with init app
    app = Flask(__name__)
    loqus_obj = LoqusDB()
    with pytest.raises(SyntaxError):
        with app.app_context():
            app.config = configs
            loqus_obj.init_app(app)


def test_init_loqusextension_init_app_with_config(loqus_exe, loqus_config):
    """Test a init a loqus extension object with flask app with version and config"""
    # GIVEN a loqusdb binary
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
        assert loqus_obj.loqusdb_binary == loqus_exe
        # THEN assert that the version is correct
        assert loqus_obj.version == version
        # THEN assert that the config is correct
        assert loqus_obj.loqusdb_config == loqus_config
