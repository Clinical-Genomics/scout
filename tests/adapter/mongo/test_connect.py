import mongomock

import scout
from scout.adapter.client import get_connection


def test_pymongo_adapter(adapter, database_name):
    """Test the pymongo adapter"""
    ##GIVEN a pymongoadapter
    ##WHEN connecting to a database
    ##THEN assert the correct database is accessed
    assert adapter.db.name == database_name


def test_connection(monkeypatch):
    def mock_mongo():
        return mongomock.MongoClient()

    monkeypatch.setattr(scout.adapter.client, "get_connection", mock_mongo)
    client = scout.adapter.client.get_connection()
    assert isinstance(client, mongomock.MongoClient)
