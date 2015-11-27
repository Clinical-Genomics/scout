import pytest
import logging
# from mongomock import MongoClient
from pymongo import MongoClient
from mongoengine import DoesNotExist

from scout.ext.backend import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)

logger = logging.getLogger()
logger.setLevel('DEBUG')

template = "[%(asctime)s] %(name)-25s %(levelname)-8s %(message)s"
formatter = logging.Formatter(template)

# add a basic STDERR handler to the logger
console = logging.StreamHandler()
console.setLevel('DEBUG')
console.setFormatter(formatter)
logger.addHandler(console)

class TestAdapter(object):
    """Test the mongo adapter"""
    
    def setup(self):
        """Setup the mongo adapter"""
        print("\nSetting up database")
        host = 'localhost'
        port = 27017
        self.db_name = 'testdatabase'
        self.client = MongoClient(
            host=host,
            port=port,
        )
        #Initialize an adapter
        self.adapter = MongoAdapter()
        #Connect to the test database
        self.adapter.connect_to_database(
            database=self.db_name, 
            host=host, 
            port=port
        )
        # setup a institute
        self.institute = Institute(
            internal_id='cust000',
            display_name='clinical'
        )
        self.institute.save()
        #setup a user
        self.user = User(
            email='john@doe.com',
            name="John Doe"
        )
        self.user.save()
        #setup a case
        case = Case(
            case_id="acase",
            display_name="acase",
            owner='cust000',
            assignee = self.user,
            collaborators = ['cust000']
        )
        case.save()
        print("Database setup\n")

    def test_get_case(self):
        
        print("Testing to get case")
        result = self.adapter.case(
            institute_id='cust000', 
            case_id='acase'
        )
        assert result.owner == 'cust000'

    def test_get_cases(self):
        
        print("Testing to get all cases for a institute")
        result = self.adapter.cases()
        for case in result:
            assert case.owner == 'cust000'

    def teardown(self):
        print('\nTeardown database')
        self.client.drop_database(self.db_name)
        print('Teardown done')
    
