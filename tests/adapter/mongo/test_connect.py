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
