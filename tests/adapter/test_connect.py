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

def test_pytest(variant_clinical_file):
    assert variant_clinical_file

