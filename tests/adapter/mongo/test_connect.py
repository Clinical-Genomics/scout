import unittest

import mongomock
import pytest
from pymongo.errors import ConnectionFailure

import scout
from scout.adapter.client import get_connection


def get_mock_client():
    return MongoClient()


def test_pymongo_adapter(adapter, database_name):
    """Test the pymongo adapter"""
    ##GIVEN a pymongoadapter
    ##WHEN connecting to a database
    ##THEN assert the correct database is accessed
    assert adapter.db.name == database_name


def test_connection(monkeypatch):
    def simple_mongo():
        return mongomock.MongoClient()

    monkeypatch.setattr(scout.adapter.client, "get_connection", simple_mongo)
    client = scout.adapter.client.get_connection()
    assert isinstance(client, mongomock.MongoClient)


# ##GIVEN a connection to a mongodatabase
# print('du')
# ##WHEN getting a mongo client
# ##THEN assert that the port is default
# print(client)
# assert False
# assert client.PORT == 27017

# def test_get_connection_uri(pymongo_client):
#     ##GIVEN a connection to a mongodatabase
#     uri = 'mongomock://'
#     client = get_connection(uri=uri)
#     ##WHEN getting a mongo client
#     ##THEN assert that the port is default
#     assert client.PORT == 27017
