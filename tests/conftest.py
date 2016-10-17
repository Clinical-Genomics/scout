import pytest
import logging

from tempfile import NamedTemporaryFile
# We will use mongomock when mongoengine allows it
from mongoengine import DoesNotExist
from configobj import ConfigObj

from vcf_parser import VCFParser

from scout.adapter import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)
from scout.commands import cli
from scout.parse import (parse_case, parse_gene_panel)
from scout.log import init_log
from scout.build import (build_institute, build_case, build_panel)


root_logger = logging.getLogger()
init_log(root_logger, loglevel='INFO')
logger = logging.getLogger(__name__)

vcf_file = "tests/fixtures/1.downsampled.vcf"
sv_path = "tests/fixtures/1.SV.vcf"
one_variant = "tests/fixtures/1.one.vcf"
one_sv = "tests/fixtures/1.one.SV.vcf"
ped_path = "tests/fixtures/1.ped"
scout_config_file = "tests/fixtures/config1.ini"
gene_list_file = "tests/fixtures/gene_lists/gene_list_test.txt"
madeline_file = "tests/fixtures/madeline.xml"

##################### File fixtures #####################
@pytest.fixture(scope='function')
def config_file(request):
    """Get the path to a config file"""
    print('')
    return scout_config_file

@pytest.fixture(scope='function')
def variant_file(request):
    """Get the path to a variant file"""
    print('')
    return vcf_file

@pytest.fixture(scope='function')
def one_variant_file(request):
    """Get the path to a variant file"""
    print('')
    return one_variant

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
def scout_configs(request, config_file):
    """Return a dictionary with scout configs"""
    print('')
    configs = ConfigObj(config_file)
    return configs

@pytest.fixture(scope='function')
def one_file_variant(request, one_variant_file):
    logger.info("Return a VCF parser with one variant")
    variant = VCFParser(infile=one_variant_file)
    return variant

@pytest.fixture(scope='function')
def one_file_sv_variant(request):
    logger.info("Return a VCF parser with one variant")
    variant = VCFParser(infile=one_sv)
    return variant

@pytest.fixture(scope='function')
def sv_variants(request, sv_file):
    logger.info("Return a VCF parser many svs")
    variants = VCFParser(infile=sv_file)
    return variants

@pytest.fixture(scope='function')
def variants(request, variant_file):
    logger.info("Return a VCF parser many svs")
    variants = VCFParser(infile=variant_file)
    return variants

##################### Case fixtures #####################

@pytest.fixture(scope='function')
def case_lines(request):
    """Get the lines for a case"""
    lines = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "337334-testset	ADM1136A1	0	0	1	1",
        "337334-testset	ADM1136A2	ADM1136A1	ADM1136A3	1	2",
        "337334-testset	ADM1136A3	0	0	2	1",
    ]
    return lines

@pytest.fixture(scope='function')
def parsed_case(request, case_lines, scout_configs):
    """Get the lines for a case"""
    owner = scout_configs['owner']
    
    case = parse_case(case_lines, owner)
    
    return case    

@pytest.fixture(scope='function')
def minimal_case(request):
    print('')
    logger.info("setup a vcf case")
    case = {
        'case_id': "337334",
        'display_name': "337334",
        'owner': 'cust000',
        'collaborators': ['cust000'],
        'individuals':[]
    }
    
    return case

@pytest.fixture(scope='function')
def case_obj(request, parsed_case):
    logger.info("Create a case obj")
    case = build_case(parsed_case)
    
    return case

##################### Institute fixtures #####################

@pytest.fixture(scope='function')
def parsed_institute(request):
    print('')
    institute = {
        'institute_id': 'cust000',
        'display_name': 'test_institute',
        'sanger_recipients': ['john@doe.com']
    }
    
    return institute

@pytest.fixture(scope='function')
def institute_obj(request, parsed_institute):
    print('')
    institute = build_institute(
        internal_id = parsed_institute['institute_id'],
        display_name = parsed_institute['display_name'],
        sanger_recipients = parsed_institute['sanger_recipients'],
    )
    return institute


##################### Adapter fixtures #####################

@pytest.fixture(scope='function')
def client(request):
    """Get a mongoadapter"""
    logger.info("Get a mongo adapter")
    mongo_client = MongoAdapter()
    
    return mongo_client

@pytest.fixture(scope='function')
def adapter(request):
    """Get an adapter connected to mongomock database"""
    database = 'test'
    host = 'localhost'
    port = 27017
    
    mongo_client = MongoAdapter()
    mongo_client.connect_to_database(
        database=database,
        host=host,
        port=port
    )
    
    def teardown():
        print('\n')
        logger.info("Deleting database")
        mongo_client.drop_database()
        logger.info("Database deleted")

    request.addfinalizer(teardown)
    
    return mongo_client

@pytest.fixture(scope='function')
def parsed_user(request, institute_obj):
    """Return user info"""
    user_info = {
        'email': 'john@doe.com', 
        'name': 'John Doe', 
        'location': None, 
        'institutes': [institute_obj],
        'roles': ['admin']
    }
    return user_info

@pytest.fixture(scope='function')
def user_obj(request, parsed_user):
    """Return a User object"""
    user = User(
      email=parsed_user['email'],
      name=parsed_user['name'],
      institutes=parsed_user['institutes']
    )
    return user

@pytest.fixture(scope='function')
def populated_database(request, adapter, institute_obj, parsed_user, case_obj):
    "Returns an adapter to a database populated with user, institute and case"
    adapter.add_institute(institute_obj)
    adapter.getoradd_user(
        email=parsed_user['email'], 
        name=parsed_user['name'],
        location=parsed_user['location'], 
        institutes=parsed_user['institutes']
    )
    adapter.add_case(case_obj)
    
    return adapter


##################### Panel fixtures #####################

@pytest.fixture(scope='function')
def panel_info(request):
    "Return one panel info as specified in tests/fixtures/config1.ini"
    panel = {
            'date': '2015-10-21',
            'file': 'tests/fixtures/gene_lists/gene_list_test.txt',
            'type': 'clinical',
            'version': '0.1',
            'name': 'Panel1',
            'full_name': 'Panel 1'
        }
    return panel

@pytest.fixture(scope='function')
def parsed_panel(request, panel_info):
    """docstring for parsed_panels"""
    owner = 'cust000'
    panel = parse_gene_panel(panel_info, owner)
    
    return panel

@pytest.fixture(scope='function')
def panel_obj(request, parsed_panel):
    """docstring for parsed_panels"""
    panel = build_panel(panel_info)

    return panel

##################### Variant fixtures #####################


@pytest.fixture(scope='function')
def variants(request):
    """Get a parser with vcf variants"""
    print('')
    variant_parser = VCFParser(infile=vcf_file)
    return variant_parser


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
