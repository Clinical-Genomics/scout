import pytest

from scout.server.app import create_app


#############################################################
###################### App fixtures #########################
#############################################################
 # use this app object to test CLI commands which use a test database

DATABASE = 'testdb'
REAL_DATABASE = 'realtestdb'


@pytest.fixture(scope='function')
def empty_mock_app(real_adapter):

    _mock_app = create_app(config=dict(TESTING=True, DEBUG=True, MONGO_DBNAME=REAL_DATABASE,
                                 DEBUG_TB_ENABLED=False, LOGIN_DISABLED=True))
    return _mock_app


@pytest.fixture
def mock_app(real_populated_database):

    _mock_app = create_app(config=dict(TESTING=True, DEBUG=True, MONGO_DBNAME=REAL_DATABASE,
                                 DEBUG_TB_ENABLED=False, LOGIN_DISABLED=True))
    return _mock_app
