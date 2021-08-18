"""Fixtures for extenstions"""
import uuid

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


@pytest.fixture
def loqus_api_variant():
    """Returns a Loqus executable instance variant"""
    variant_found = {
        "chrom": "1",
        "observations": 1,
        "families": ["643594"],
        "nr_cases": 1,
        "start": 880086,
        "end": 880087,
        "ref": "T",
        "alt": "C",
        "homozygote": 0,
        "hemizygote": 0,
        "status_code": 200,  # Added by Scout after receiving response
    }
    return variant_found


@pytest.fixture
def loqus_exe_variant():
    """Returns a Loqus executable instance variant"""
    variant_found = (
        b'{"homozygote": 0, "hemizygote": 0, "observations": 1, "chrom": "1", "start": '
        b'235918688, "end": 235918693, "ref": "CAAAAG", "alt": "C", "families": ["643594"],'
        b' "total": 3}'
    )
    return variant_found


@pytest.fixture
def loqus_exe_app(loqus_exe, loqus_config, real_database_name):
    """Return an app connected to LoqusDB via Loqus executable"""

    app = create_app(
        config=dict(
            SECRET_KEY=str(uuid.uuid4()),
            TESTING=True,
            MONGO_DBNAME=real_database_name,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
            WTF_CSRF_ENABLED=False,
            LOQUSDB_SETTINGS={
                "binary_path": loqus_exe,
                "config_path": loqus_config,
            },
        )
    )
    return app


@pytest.fixture
def loqus_api_app(real_database_name):
    """Return an app connected to LoqusDB via REST API"""

    app = create_app(
        config=dict(
            SECRET_KEY=str(uuid.uuid4()),
            TESTING=True,
            MONGO_DBNAME=real_database_name,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
            WTF_CSRF_ENABLED=False,
            LOQUSDB_SETTINGS={"api_url": "url/to/loqus/api"},
        )
    )
    return app


@pytest.fixture
def gens_app(real_database_name):
    """Return an app containing the Gens extension"""

    app = create_app(
        config=dict(
            SECRET_KEY=str(uuid.uuid4()),
            TESTING=True,
            MONGO_DBNAME=real_database_name,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
            WTF_CSRF_ENABLED=False,
            GENS_HOST="127.0.0.1",
            GENS_PORT=5000,
        )
    )
    return app
