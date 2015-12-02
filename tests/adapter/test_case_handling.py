import pytest
import logging
# from mongomock import MongoClient
from pymongo import MongoClient
from mongoengine import DoesNotExist

from scout.ext.backend import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)

logger = logging.getLogger(__name__)


def test_get_cases(setup_database, get_case):
    print('')
    logger.info("Testing to get all cases")
    result = setup_database.cases()
    for case in result:
        assert case.owner == 'cust000'
    logger.info("All cases checked")

def test_get_case(setup_database, get_case):
    print('')
    logger.info("Testing to get case")
    result = setup_database.case(
        institute_id='cust000',
        case_id='acase'
    )
    assert result.owner == 'cust000'

def test_add_case(setup_database, get_case_info):
    print('')
    logger.info("Testing to add a case")
    setup_database.add_case(
        case_lines=get_case_info['case_lines'], 
        case_type=get_case_info['case_type'], 
        owner=get_case_info['owner'],
        scout_configs=get_case_info['scout_configs']
    )
    result = setup_database.case(
        institute_id='cust000',
        case_id='636808'
    )
    assert result.owner == 'cust000'
    for individual in result['individuals']:
        assert individual['individual_id'] in set(
                    get_case_info['scout_configs']['individuals'].keys())

