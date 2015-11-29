import pytest
import logging
# from mongomock import MongoClient
from pymongo import MongoClient
from mongoengine import DoesNotExist

from scout.ext.backend import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)


from scout.log import init_log
root_logger = logging.getLogger()
init_log(root_logger, loglevel='DEBUG')
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')
def setup_database(request):
    """Setup the mongo adapter"""
    print('')
    logger.info("Setting up database")
    host = 'localhost'
    port = 27017
    db_name = 'testdatabase'
    client = MongoClient(
        host=host,
        port=port,
    )
    #Initialize an adapter
    adapter = MongoAdapter()
    #Connect to the test database
    adapter.connect_to_database(
        database=db_name, 
        host=host, 
        port=port
    )
    # setup a institute
    institute = Institute(
        internal_id='cust000',
        display_name='clinical'
    )
    institute.save()
    #setup a user
    user = User(
        email='john@doe.com',
        name="John Doe"
    )
    user.save()
    #setup a case
    case = Case(
        case_id="acase",
        display_name="acase",
        owner='cust000',
        assignee = user,
        collaborators = ['cust000']
    )
    case.save()
    
    adapter.create_event(
        institute=institute,
        case=case,
        user=user,
        link="aurl",
        category='case',
        verb="assign",
        subject='acase'
    )
    
    logger.info("Database setup")
    def teardown():
        print('\n')
        logger.info('Teardown database')
        client.drop_database(db_name)
        logger.info('Teardown done')
    request.addfinalizer(teardown)
    return adapter

@pytest.fixture(scope='function')
def get_institute(request):
    # setup a institute
    institute = Institute(
        internal_id='cust000',
        display_name='clinical'
    )
    return institute

def test_get_events(setup_database, get_institute):
    logger.info("Testing to get event")
    result = setup_database.events(institute=get_institute)
    for res in result:
        assert res.link == 'aurl'

