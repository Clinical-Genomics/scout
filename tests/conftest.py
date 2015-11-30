import pytest
import logging
# We will use mongomock when mongoengine allows it
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

@pytest.fixture(scope='session')
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
    print('')
    logger.info("setup a institute")
    institute = Institute(
        internal_id='cust000',
        display_name='clinical'
    )
    logger.info("Adding institute to database")
    institute.save()
    def teardown():
        print('\n')
        logger.info('Removing institute')
        institute.delete()
        logger.info('Institute removed')
    request.addfinalizer(teardown)
    
    return institute

@pytest.fixture(scope='function')
def get_user(request):
    logger.info("setup a user")
    user = User(
        email='john@doe.com',
        name="John Doe"
    )
    logger.info("Adding user to database")
    user.save()
    def teardown():
        print('\n')
        logger.info('Removing user')
        user.delete()
        logger.info('user removed')
    request.addfinalizer(teardown)
    
    return user

@pytest.fixture(scope='function')
def get_case(request):
    logger.info("setup a case")
    case = Case(
        case_id="acase",
        display_name="acase",
        owner='cust000',
        collaborators = ['cust000']
    )
    logger.info("Adding case to database")
    case.save()
    def teardown():
        print('\n')
        logger.info('Removing case')
        case.delete()
        logger.info('Case removed')
    request.addfinalizer(teardown)
    
    return case

@pytest.fixture(scope='function')
def get_variant(request, get_institute):
    logger.info("setup a variant")
    variant = Variant(
        document_id = "document_id",
        variant_id = "variant_id",
        display_name = "display_name",
        variant_type = 'research',
        case_id = 'case_id',
        chromosome = '1',
        position = 10,
        reference = "A",
        alternative = "C",
        rank_score = 10.0,
        variant_rank = 1,
        institute = get_institute,
    )
    logger.info("Adding variant to database")
    variant.save()
    def teardown():
        print('\n')
        logger.info('Removing variant')
        variant.delete()
        logger.info('Case variant')
    request.addfinalizer(teardown)
    
    return variant

