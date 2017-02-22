import pytest
from pymongo.errors import ConnectionFailure
from scout.adapter.client import get_connection

def test_pymongo_adapter(pymongo_adapter):
    """Test the pymongo adapter"""
    ##GIVEN a pymongoadapter
    ##WHEN connecting to a database
    ##THEN assert the correct database is accessed
    assert pymongo_adapter.db.name == 'testdb'

def test_get_connection():
    ##GIVEN a connection to a mongodatabase
    client = get_connection()
    ##WHEN getting a mongo client
    ##THEN assert that the port is default
    assert client.PORT == 27017

def test_pytest(variant_clinical_file):
    assert variant_clinical_file

