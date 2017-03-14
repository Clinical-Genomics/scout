import pytest
from pymongo.errors import ConnectionFailure
from scout.adapter.client import get_connection

def test_pymongo_adapter(adapter, database_name):
    """Test the pymongo adapter"""
    ##GIVEN a pymongoadapter
    ##WHEN connecting to a database
    ##THEN assert the correct database is accessed
    assert adapter.db.name == database_name

def test_get_connection():
    ##GIVEN a connection to a mongodatabase
    client = get_connection()
    ##WHEN getting a mongo client
    ##THEN assert that the port is default
    assert client.PORT == 27017

# def test_get_connection_uri(pymongo_client):
#     ##GIVEN a connection to a mongodatabase
#     uri = 'mongomock://'
#     client = get_connection(uri=uri)
#     ##WHEN getting a mongo client
#     ##THEN assert that the port is default
#     assert client.PORT == 27017


