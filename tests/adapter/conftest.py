import logging

import pytest

from mongomock import MongoClient

from pymongo import MongoClient as RealClient

from scout.adapter.pymongo import MongoAdapter as PymongoAdapter

logger = logging.getLogger(__name__)

@pytest.fixture(scope='function')
def client(request):
    """Get a mongomock client"""
    logger.info("Get a mongomock client")
    mock_client = MongoClient()

    return mock_client

@pytest.fixture(scope='function')
def real_client(request):
    """Get a mongomock client"""
    logger.info("Get a mongomock client")
    real_client = RealClient()
    
    def teardown():
        print('\n')
        logger.info("Deleting database")
        real_client.drop_database('testdb')
        logger.info("Database deleted")

    request.addfinalizer(teardown)

    return real_client

@pytest.fixture(scope='function')
def real_pymongo_adapter(request, real_client):
    """Get a mongoadapter"""
    logger.info("Get a mongo adapter that uses testdb as database")
    database = real_client['testdb']

    adapter = PymongoAdapter(database)

    return adapter


@pytest.fixture(scope='function')
def pymongo_adapter(request, client):
    """Get a mongoadapter"""
    logger.info("Get a mongo adapter that uses testdb as database")
    database = client['testdb']
    
    adapter = PymongoAdapter(database)

    return adapter
