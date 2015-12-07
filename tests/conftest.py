import pytest
import logging

from tempfile import NamedTemporaryFile
# We will use mongomock when mongoengine allows it
# from mongomock import MongoClient
from pymongo import MongoClient
from mongoengine import DoesNotExist
from configobj import ConfigObj

from vcf_parser import VCFParser

from scout.ext.backend import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)
from scout.commands import cli

from scout.log import init_log
root_logger = logging.getLogger()
init_log(root_logger, loglevel='INFO')
logger = logging.getLogger(__name__)

vcf_file = "tests/fixtures/337334.clinical.vcf"
one_variant = "tests/fixtures/337334.one_variant.clinical.vcf"
ped_file = "tests/fixtures/337334.ped"
scout_config = "tests/fixtures/scout_config_test.ini"
gene_list_file = "tests/fixtures/gene_lists/gene_list_test.txt"
madeline_file = "tests/fixtures/madeline.xml"

@pytest.fixture(scope='function')
def variant_file(request):
    """Get the path to a variant file"""
    print('')
    return vcf_file

@pytest.fixture(scope='function')
def ped_file(request):
    """Get the path to a ped file"""
    print('')
    return ped_file


@pytest.fixture(scope='function')
def vcf_case(request):
    logger.info("setup a vcf case")
    case = Case(
        case_id="337334",
        display_name="337334",
        owner='cust000',
        collaborators = ['cust000']
    )
    
    return case

@pytest.fixture(scope='function')
def compound_variant(request):
    logger.info("setup a compound variant")
    variant = {
        'variant_id':'7_117175580_C_A',
        'compound_variants':{
            "337334":[
                {'variant_id':'7_117175579_AT_A',
                'compound_score': 32}
            ]
        }
    }
    
    return variant

@pytest.fixture(scope='function')
def variants(request):
    """Get a parser with vcf variants"""
    print('')
    variant_parser = VCFParser(infile=vcf_file)
    return variant_parser

@pytest.fixture(scope='session')
def database_setup(request):
    """Get a config file with mongodb arguments"""
    print('')
    logger.info("Setting up database configs")
    config_file = NamedTemporaryFile(delete=False, mode='w')
    
    host = 'localhost'
    port = 27017
    db_name = 'testdatabase'
    
    config_file.write("mongodb = {0}\n".format(db_name))
    config_file.write("host = {0}\n".format(host))
    config_file.write("port = 27017\n".format(db_name))
    
    config_file.close()
    
    logger.info("Database configs setup")
    def teardown():
        print('\n')
        client = MongoClient()
        logger.info('Teardown database')
        client.drop_database(db_name)
        logger.info('Teardown done')
    request.addfinalizer(teardown)
    return config_file.name

@pytest.fixture(scope='session')
def setup_loaded_database(request):
    """Setup a mongo databse with loaded variants"""
    print('')
    logger.info("Setting up database and populate it")
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
    scout_configs = ConfigObj(scout_config)
    
    case = adapter.add_case(
        case_lines=open(scout_configs['ped'], 'r'),
        case_type='ped', 
        owner=scout_configs['owner'], 
        scout_configs=scout_configs
    )
    
    adapter.add_variants(
        vcf_file=scout_configs['load_vcf'], 
        variant_type='clinical',
        case=case,
    )
    
    logger.info("Database setup")
    def teardown():
        print('\n')
        logger.info('Teardown database')
        client.drop_database(db_name)
        logger.info('Teardown done')
    request.addfinalizer(teardown)
    return adapter


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
def get_case_info(request):
    logger.info("Get the necessary information to build a case")
    case = {}
    case['case_lines'] = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "636808	ADM1059A1	0	0	1	1",
        "636808	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
        "636808	ADM1059A3	0	0	2	1",
    ]
    
    case['scout_configs'] = {
        'load': True,
        'load_vcf':vcf_file,
        'analysis_type': 'wes',
        'rank_model_version': '1.12',
        'owner': 'cust000',
        'collaborators': [],
        'analysis_date': '2015-11-23 14:00:46',
        'human_genome_version': 37,
        'human_genome_build': 'GRCh',
        'madeline': madeline_file,
        'ped': ped_file,
        'default_panels': ['IEM'],
        'igv_vcf': vcf_file,
        'gene_lists':{
                'Panel1': {
                    'date': '2015-10-21',
                    'file': gene_list_file,
                    'version': 0.1,
                    'name': 'Panel1',
                    'full_name': "Panel 1",
                    }
                },
        'individuals':{
            'ADM1059A3': {
                'capture_kit': ['Agilent_SureSelectCRE.V1'],
                'bam_path': 'abam.bam',
                'name': 'ADM1059A3'
                },
            'ADM1059A2':{
                'capture_kit': ['Agilent_SureSelectCRE.V1,'],
                'bam_path': 'abam.bam',
                'name': 'ADM1059A2'
                },
            'ADM1059A1':{
                'capture_kit': ['Agilent_SureSelectCRE.V1'],
                'bam_path': 'abam.bam',
                'name': 'ADM1059A1'
                }
            }
    }
    case['case_type'] = 'ped'
    case['owner'] = 'cust000'

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

