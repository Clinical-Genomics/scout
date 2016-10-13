import pytest
import logging

from tempfile import NamedTemporaryFile
# We will use mongomock when mongoengine allows it
# from mongomock import MongoClient
# from pymongo import MongoClient
from mongoengine import DoesNotExist
from configobj import ConfigObj

from vcf_parser import VCFParser

from scout.adapter import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)
from scout.commands import cli

from scout.log import init_log
root_logger = logging.getLogger()
init_log(root_logger, loglevel='INFO')
logger = logging.getLogger(__name__)

vcf_file = "tests/fixtures/1.downsampled.vcf"
sv_path = "tests/fixtures/1.SV.vcf"
one_variant = "tests/fixtures/1.one.vcf"
one_sv = "tests/fixtures/1.one.SV.vcf"
ped_path = "tests/fixtures/1.ped"
scout_config = "tests/fixtures/config1.ini"
gene_list_file = "tests/fixtures/gene_lists/gene_list_test.txt"
madeline_file = "tests/fixtures/madeline.xml"

@pytest.fixture(scope='function')
def variant_file(request):
    """Get the path to a variant file"""
    print('')
    return vcf_file

@pytest.fixture(scope='function')
def sv_file(request):
    """Get the path to a variant file"""
    print('')
    return sv_path

@pytest.fixture(scope='function')
def ped_file(request):
    """Get the path to a ped file"""
    print('')
    return ped_path


@pytest.fixture(scope='function')
def minimal_case(request):
    logger.info("setup a vcf case")
    case = {
        'case_id': "337334",
        'display_name': "337334",
        'owner': 'cust000',
        'collaborators': ['cust000'],
    }
    
    return case

@pytest.fixture(scope='function')
def one_file_variant(request):
    logger.info("Return a VCF parser with one variant")
    variant = VCFParser(infile=one_variant)
    return variant

@pytest.fixture(scope='function')
def one_file_sv_variant(request):
    logger.info("Return a VCF parser with one variant")
    variant = VCFParser(infile=one_sv)
    return variant



@pytest.fixture(scope='function')
def parsed_case(request):
    logger.info("setup a vcf case")
    case = {
        'case_id': "337334",
        'display_name': "337334",
        'owner': 'cust000',
        'collaborators': ['cust000'],
        'individuals':[
            {
                'ind_id': 'ADM1136A1',
                'father': '0',
                'mother': '0',
                'display_name': 'ADM1136A1',
                'sex': '1',
                'phenotype': 1
            },
            {
                'ind_id': 'ADM1136A2',
                'father': 'ADM1136A1',
                'mother': 'ADM1136A3',
                'display_name': 'ADM1136A2',
                'sex': '1',
                'phenotype': 2
            },
            {
                'ind_id': 'ADM1136A3',
                'father': '0',
                'mother': '0',
                'display_name': 'ADM1136A3',
                'sex': '2',
                'phenotype': 1
            },
            
        ]
    }
    
    return case


@pytest.fixture(scope='function')
def case_obj(request):
    logger.info("Create a case obj")
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

@pytest.fixture(scope='function')
def client(request):
    """Get a mongoadapter"""
    logger.info("Get a mongo adapter")
    host = 'mongomock://localhost'
    port = 27019
    client = MongoAdapter()
    
    return client

@pytest.yield_fixture(scope='function')
def adapter(request):
    """Get an adapter connected to mongomock database"""
    client = MongoAdapter()
    # client.connect_to_database(
    #     database='mongotest',
    #     host='mongomock://localhost',
    #     port=27019,
    #     username=None,
    #     password=None
    # )
    client.connect_to_database(
        database='test', 
    )
    yield client

    print('\n')
    logger.info('Teardown database')
    client.drop_database()
    for case in client.cases():
        print(case)
    logger.info('Teardown done')

@pytest.fixture(scope='function')
def minimal_snv(request):
    """Simulate a variant dictionary from vcf parser"""
    variant = {
        'CHROM':'1',
        'POS':'27232819',
        'REF':'A',
        'ALT':'T',
        'ID':'rs1',
        'FILTER':'PASS',
        'QUAL':'164',
        'info_dict': {},
        'compound_variants': {},
        'vep_info': {},
        
    }
    return variant

@pytest.fixture(scope='function')
def minimal_sv(request):
    """Simulate a variant dictionary from vcf parser"""
    variant = {
        'CHROM':'1',
        'POS':'10',
        'REF':'A',
        'ALT':'C',
        'ID':'rs1',
        'FILTER':'PASS',
        'QUAL':'1000',
        'INFO':'.',
        'info_dict': {},
        'compound_variants': {},
        'vep_info': {},
        'rank_scores': {'15026-miptest': '-2'},
        'variant_id': '1_27232819_T_T]16:89585536]',
        'info_dict':{
            'Ensembl_transcript_to_refseq_transcript': ["NUDC:ENST00000321265>NM_006600/"\
            "XM_005245726|ENST00000435827|ENST00000452707|ENST00000484772"],
            'Gene_description': ['NUDC:nudC_nuclear_distribution_protein'],
            'MATEID':['MantaBND:454:0:1:0:0:0:1'],
            'SVTYPE':['BND'],
        },
        'vep_info': {
            u'T]16': [
                {
                    'APPRIS': '',
                    'Allele': 'T]16',
                    'Amino_acids': '',
                    'BIOTYPE': 'protein_coding',
                    'CANONICAL': '',
                    'CCDS': '',
                    'CDS_position': '',
                    'Codons': '',
                    'Consequence': 'intron_variant',
                    'DISTANCE': '',
                    'DOMAINS': '',
                    'ENSP': 'ENSP00000404020',
                    'EXON': '',
                    'Existing_variation': '',
                    'FLAGS': 'cds_end_NF',
                    'Feature': 'ENST00000435827',
                    'Feature_type': 'Transcript',
                    'Gene': 'ENSG00000090273',
                    'HGNC_ID': '8045',
                    'HGVS_OFFSET': '',
                    'HGVSc': '',
                    'HGVSp': '',
                    'HIGH_INF_POS': '',
                    'IMPACT': 'MODIFIER',
                    'INTRON': '2/6',
                    'MOTIF_NAME': '',
                    'MOTIF_POS': '',
                    'MOTIF_SCORE_CHANGE': '',
                    'PolyPhen': '',
                    'Protein_position': '',
                    'SIFT': '',
                    'STRAND': '1',
                    'SWISSPROT': '',
                    'SYMBOL': 'NUDC',
                    'SYMBOL_SOURCE': 'HGNC',
                    'TREMBL': '',
                    'TSL': '',
                    'UNIPARC': 'UPI0002A475AB',
                    'cDNA_position': ''
                }
            ],
            'T]16:89585536]': []
        }
    }
    return variant

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
