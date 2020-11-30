"""Fixtures for CLI tests"""
import pathlib

import pytest

from scout.demo.resources import demo_files
from scout.server.app import create_app

#############################################################
###################### App fixtures #########################
#############################################################
# use this app object to test CLI commands which use a test database

DATABASE = "testdb"
REAL_DATABASE = "realtestdb"


@pytest.fixture(scope="function", name="demo_files")
def fixture_demo_files():
    """Return a dictionary with paths to the demo files"""
    return demo_files


@pytest.fixture(scope="function")
def bam_path():
    """Return the path to a small existing bam file"""
    _path = pathlib.Path("tests/fixtures/bams/reduced_mt.bam")
    return _path


@pytest.fixture(scope="function")
def empty_mock_app(real_adapter):
    """Return the path to a mocked app object without any data"""
    _mock_app = create_app(
        config=dict(
            TESTING=True,
            DEBUG=True,
            MONGO_DBNAME=REAL_DATABASE,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
        )
    )
    return _mock_app
