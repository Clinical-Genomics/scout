# -*- coding: utf-8 -*-
import pytest
import logging

from vcf_parser import VCFParser
import yaml

from scout.adapter import MongoAdapter
from scout.models import Variant, Case, Event, PhenotypeTerm, Institute, User
from scout.parse import (parse_case, parse_gene_panel, parse_variant, 
                         parse_hgnc_genes, parse_ensembl_transcripts)
from scout.log import init_log
from scout.build import (build_institute, build_case, build_panel, build_variant)


root_logger = logging.getLogger()
init_log(root_logger, loglevel='INFO')
logger = logging.getLogger(__name__)

vcf_file = "tests/fixtures/1.downsampled.vcf"
sv_path = "tests/fixtures/1.SV.vcf"
one_variant = "tests/fixtures/1.one.vcf"
one_sv = "tests/fixtures/1.one.SV.vcf"
ped_path = "tests/fixtures/1.ped"
scout_config_file = "tests/fixtures/config1.ini"
scout_yaml_config = 'tests/fixtures/config1.yaml'
gene_list_file = "tests/fixtures/gene_lists/gene_list_test.txt"
madeline_file = "tests/fixtures/madeline.xml"

hgnc_path = "tests/fixtures/resources/hgnc_complete_set.txt"
ensembl_transcript_path = "tests/fixtures/resources/ensembl_transcripts_37.txt"


##################### File fixtures #####################
@pytest.fixture
def config_file(request):
    """Get the path to a config file"""
    print('')
    return scout_yaml_config

@pytest.fixture
def hgnc_file(request):
    """Get the path to a hgnc file"""
    print('')
    return hgnc_path

@pytest.fixture
def transcripts_file(request):
    """Get the path to a ensembl transcripts file"""
    print('')
    return ensembl_transcript_path

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
def scout_config(request, config_file):
    """Return a dictionary with scout configs"""
    print('')
    with open(config_file) as in_handle:
        data = yaml.load(in_handle)
    return data


##################### Gene fixtures #####################

@pytest.fixture
def hgnc_handle(request, hgnc_file):
    """Get a file handle to a hgnc file"""
    print('')
    return open(hgnc_file, 'r')

@pytest.fixture
def hgnc_genes(request, hgnc_handle):
    """Get a dictionary with hgnc genes"""
    print('')
    return parse_hgnc_genes(hgnc_handle)

@pytest.fixture
def transcripts_handle(request, transcripts_file):
    """Get a file handle to a ensembl transcripts file"""
    print('')
    return open(transcripts_file, 'r')

@pytest.fixture
def transcripts(request, transcripts_handle):
    """Get a file handle to a ensembl transcripts file"""
    print('')
    return parse_ensembl_transcripts(transcripts_handle)


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
def parsed_case(request, case_lines, scout_config):
    """Get the lines for a case"""
    case = parse_case(scout_config, ped=case_lines)
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
        'individuals': []
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
        internal_id=parsed_institute['institute_id'],
        display_name=parsed_institute['display_name'],
        sanger_recipients=parsed_institute['sanger_recipients'],
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


@pytest.fixture(scope='function')
def variant_database(request, adapter, institute_obj, parsed_user, case_obj,
                     variant_objs, sv_variant_objs):
    """Returns an adapter to a database populated with user, institute, case
       and variants"""
    adapter.add_institute(institute_obj)
    adapter.getoradd_user(
        email=parsed_user['email'],
        name=parsed_user['name'],
        location=parsed_user['location'],
        institutes=parsed_user['institutes']
    )
    adapter.add_case(case_obj)

    # Load variants
    for variant in variant_objs:
        adapter.load_variant(variant)

    # Load sv variants
    for variant in sv_variant_objs:
        adapter.load_variant(variant)

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

@pytest.fixture(scope='function')
def parsed_variant(request, one_file_variant, parsed_case):
    """Return a parsed variant"""
    print('')
    for variant in one_file_variant:
        variant_dict = parse_variant(variant, parsed_case)
    return variant_dict

@pytest.fixture(scope='function')
def parsed_sv_variant(request, one_file_sv_variant, parsed_case):
    """Return a parsed variant"""
    print('')
    for variant in one_file_sv_variant:
        variant_dict = parse_variant(variant, parsed_case)
    return variant_dict

@pytest.fixture(scope='function')
def parsed_variants(request, variants, parsed_case):
    """Get a generator with parsed variants"""
    print('')
    return (parse_variant(variant, parsed_case) for variant in variants)

@pytest.fixture(scope='function')
def parsed_sv_variants(request, sv_variants, parsed_case):
    """Get a generator with parsed variants"""
    print('')
    return (parse_variant(variant, parsed_case) for variant in sv_variants)

@pytest.fixture(scope='function')
def variant_objs(request, parsed_variants, institute_obj):
    """Get a generator with parsed variants"""
    print('')
    return (build_variant(variant, institute_obj)
            for variant in parsed_variants)

@pytest.fixture(scope='function')
def sv_variant_objs(request, parsed_sv_variants, institute_obj):
    """Get a generator with parsed variants"""
    print('')
    return (build_variant(variant, institute_obj)
            for variant in parsed_sv_variants)



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
