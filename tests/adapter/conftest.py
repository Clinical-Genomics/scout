import logging

import pytest

from mongomock import MongoClient

from pymongo import MongoClient as RealClient

from scout.adapter.mongo import MongoAdapter as PymongoAdapter

from mongoengine import connect

logger = logging.getLogger(__name__)

DATABASE = 'testdb'

# @pytest.fixture(scope='function')
# def client(request):
#     """Get a mongomock client"""
#     logger.info("Get a mongomock client")
#     mock_client = MongoClient()
#
#     return mock_client

# @pytest.fixture(scope='function')
# def real_client(request):
#     """Get a mongomock client"""
#     logger.info("Get a real mongo client")
#     real_client = RealClient()
#
#     def teardown():
#         print('\n')
#         logger.info("Deleting database")
#         real_client.drop_database(DATABASE)
#         logger.info("Database deleted")
#
#     request.addfinalizer(teardown)
#
#     return real_client
#
# @pytest.fixture(scope='function')
# def real_pymongo_adapter(request, real_client):
#     """Get a mongoadapter"""
#     logger.info("Get a mongo adapter that uses testdb as database")
#     database = real_client[DATABASE]
#     adapter = PymongoAdapter(database)
#
#     logger.info("Connecting the mongoengine adapter")
#     # adapter.mongoengine_adapter.connect_to_database('testdb')
#
#     return adapter
#
#
# @pytest.fixture(scope='function')
# def pymongo_adapter(request, client):
#     """Get a mongoadapter"""
#     logger.info("Get a mongo adapter that uses testdb as database")
#     database = client[DATABASE]
#
#     adapter = PymongoAdapter(database)
#
#     return adapter
