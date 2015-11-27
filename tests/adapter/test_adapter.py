import pytest

from mongomock import MongoClient
from mongoengine import DoesNotExist

from scout.ext.backend import MongoAdapter
from scout.models import Institute



class TestAdapter(object):
    """Test the mongo adapter"""
    
    def setup(self):
        """Setup the mongo adapter"""
        host = 'localhost'
        port = 27017
        db = 'testdatabase'
        client = MongoClient(
            host=host,
            port=port,
        )
        database = client[db]
        #Initialize an adapter
        self.adapter = MongoAdapter()
        #Connect to the test database
        self.adapter.connect_to_database(
            database="testdatabase", 
            host=host, 
            port=port
        )
        #Insert an institute in the database
        one_institute = Institute(
            internal_id='cust000',
            display_name='clinical' 
        )
        one_institute.save()
        
    def test_get_institute(self):
        institute_id = 'cust000'
        display_name = 'clinical'
        result = self.adapter.institute(institute_id=institute_id)
        assert result.internal_id == institute_id
        assert result.display_name == display_name
    
    def test_get_non_existing_institute(self):
        institute_id = 'non_existing'
        
        result = self.adapter.institute(institute_id=institute_id)
        assert result == None
