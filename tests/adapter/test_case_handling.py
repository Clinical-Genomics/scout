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

def test_add_case(setup_database):
    print('')
    logger.info("Testing to add a case")
    case_lines = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "636808	ADM1059A1	0	0	1	1",
        "636808	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
        "636808	ADM1059A3	0	0	2	1",
    ]
    scout_config = {
        'load': True,
        'load_vcf':'test_vcf',
        'analysis_type': 'wes',
        'rank_model_version': '1.12',
        'owner': 'cust000',
        'collaborators': [],
        'analysis_date': '2015-11-23 14:00:46',
        'human_genome_version': 37,
        'human_genome_build': 'GRCh',
        'madeline': 'madeline.xml',
        'ped': 'pedigree.ped',
        'default_panels': 'IEM',
        'igv_vcf': 'test_vcf',
        'gene_lists':{
                'PIDCAD': {
                    'date': '2015-10-21',
                    'file': 'gene_list.txt',
                    'version': 7.2,
                    'name': 'PIDCAD',
                    'full_name': "PID Candidates",
                    }
                },
        'individuals':{
            'ADM1136A3': {
                'capture_kit': ['Agilent_SureSelectCRE.V1'],
                'bam_path': 'abam.bam',
                'name': 'ADM1136A3'
                },
            'ADM1136A2':{
                'capture_kit': ['Agilent_SureSelectCRE.V1,'],
                'bam_path': 'abam.bam',
                'name': 'ADM1136A2'
                },
            'ADM1136A1':{
                'capture_kit': ['Agilent_SureSelectCRE.V1'],
                'bam_path': 'abam.bam',
                'name': 'ADM1136A1'
                }
            }
    }
    setup_database.add_case(
        case_lines=case_lines, 
        case_type='ped', 
        owner='cust000',
        scout_configs=scout_config
    )
    result = setup_database.case(
        institute_id='cust000',
        case_id='636808'
    )
    assert result.owner == 'cust000'

