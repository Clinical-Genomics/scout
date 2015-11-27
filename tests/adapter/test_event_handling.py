import pytest

# from mongomock import MongoClient
from pymongo import MongoClient
from mongoengine import DoesNotExist

from scout.ext.backend import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)



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
        self.case = Case(
            case_id="acase",
            display_name="acase",
            owner='cust000',
            assignee = self.user
        )
        self.case.save()
        print("Database setup")


    def test_insert_event(self):
        self.adapter.create_event(
            institute=self.institute,
            case=self.case,
            user=self.user,
            link="aurl",
            category='case',
            verb="assign",
            subject='acase'
        )
        assert True
    
    def test_get_events(self):
        print("Testing to get event\n")
        print("Creating event")
        self.adapter.create_event(
            institute=self.institute,
            case=self.case,
            user=self.user,
            link="aurl",
            category='case',
            verb="assign",
            subject='acase'
        )
        print("Event created")
        assert True
        result = self.adapter.events(institute=self.institute)
        for res in result:
            print('result', res)
            assert res.link == 'aurl'
    
    
    def test_nothing(self):
        assert True

    def teardown(self):
        print('\nTeardown database')
        self.client.drop_database(self.db_name)
        print('Teardown done')
    
