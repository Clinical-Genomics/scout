# -*- coding: utf-8 -*-
import pytest
import logging
import datetime

from scout.utils.handle import get_file_handle

from vcf_parser import VCFParser
import yaml

from scout.adapter import MongoAdapter
from scout.models import Variant, Case, Event, PhenotypeTerm, Institute, User
from scout.parse.case import parse_case
from scout.parse.panel import parse_gene_panel
from scout.parse.variant import parse_variant
from scout.parse.hgnc import parse_hgnc_genes
from scout.parse.ensembl import parse_ensembl_transcripts
from scout.parse.exac import parse_exac_genes
from scout.parse.hpo import (parse_hpo_phenotypes, parse_hpo_genes, parse_hpo_diseases)

from scout.utils.link import link_genes
from scout.log import init_log
from scout.build import (build_institute, build_case, build_panel, build_variant)
from scout.load import (load_hgnc_genes, load_panel)

root_logger = logging.getLogger()
init_log(root_logger, loglevel='INFO')
logger = logging.getLogger(__name__)

vcf_research_file = "tests/fixtures/643594.research.vcf"
sv_research_path = "tests/fixtures/1.SV.vcf"
vcf_clinical_file = "tests/fixtures/643594.clinical.vcf"
sv_clinical_path = "tests/fixtures/643594.clinical.SV.vcf"
ped_path = "tests/fixtures/1.ped"
scout_yaml_config = 'tests/fixtures/643594.config.yaml'
panel_1_path = "tests/fixtures/gene_lists/panel_1.txt"
madeline_file = "tests/fixtures/madeline.xml"

hgnc_path = "tests/fixtures/resources/hgnc_reduced_set.txt"
ensembl_transcript_path = "tests/fixtures/resources/ensembl_transcripts_reduced.txt"
exac_genes_path = "tests/fixtures/resources/forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt"
hpo_genes_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype_reduced.txt"
hpo_terms_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes_reduced.txt"
hpo_disease_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes_reduced.txt"

##################### File fixtures #####################
@pytest.fixture
def config_file(request):
    """Get the path to a config file"""
    print('')
    return scout_yaml_config

@pytest.fixture
def panel_1_file(request):
    """Get the path to a config file"""
    print('')
    return panel_1_path

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

@pytest.fixture
def exac_file(request):
    """Get the path to a exac genes file"""
    print('')
    return exac_genes_path

@pytest.fixture
def hpo_genes_file(request):
    """Get the path to the hpo genes file"""
    print('')
    return hpo_genes_path

@pytest.fixture
def hpo_terms_file(request):
    """Get the path to the hpo terms file"""
    print('')
    return hpo_terms_path

@pytest.fixture
def hpo_disease_file(request):
    """Get the path to the hpo disease file"""
    print('')
    return hpo_disease_path

@pytest.fixture(scope='function')
def variant_clinical_file(request):
    """Get the path to a variant file"""
    print('')
    return vcf_clinical_file

@pytest.fixture(scope='function')
def sv_clinical_file(request):
    """Get the path to a variant file"""
    print('')
    return sv_clinical_path


@pytest.fixture(scope='function')
def ped_file(request):
    """Get the path to a ped file"""
    print('')
    return ped_path


@pytest.fixture(scope='function')
def scout_config(request, config_file):
    """Return a dictionary with scout configs"""
    print('')
    in_handle = get_file_handle(config_file)
    data = yaml.load(in_handle)
    return data


##################### Gene fixtures #####################

@pytest.fixture
def hgnc_handle(request, hgnc_file):
    """Get a file handle to a hgnc file"""
    print('')
    return get_file_handle(hgnc_file)

@pytest.fixture
def hgnc_genes(request, hgnc_handle):
    """Get a dictionary with hgnc genes"""
    print('')
    return parse_hgnc_genes(hgnc_handle)

@pytest.fixture
def transcripts_handle(request, transcripts_file):
    """Get a file handle to a ensembl transcripts file"""
    print('')
    return get_file_handle(transcripts_file)

@pytest.fixture
def transcripts(request, transcripts_handle):
    """Get the parsed ensembl transcripts"""
    print('')
    return parse_ensembl_transcripts(transcripts_handle)

@pytest.fixture
def exac_handle(request, exac_file):
    """Get a file handle to a ensembl gene file"""
    print('')
    return get_file_handle(exac_file)

@pytest.fixture
def exac_genes(request, exac_handle):
    """Get the parsed exac genes"""
    print('')
    return parse_exac_genes(exac_handle)

@pytest.fixture
def hpo_genes_handle(request, hpo_genes_file):
    """Get a file handle to a hpo gene file"""
    print('')
    return get_file_handle(hpo_genes_file)

@pytest.fixture
def hpo_genes(request, hpo_genes_handle):
    """Get the exac genes"""
    print('')
    return parse_hpo_genes(hpo_genes_handle)

@pytest.fixture
def genes(request, transcripts_handle, hgnc_handle, exac_handle, 
          hpo_genes_handle):
    """Get a dictionary with the linked genes"""
    print('')
    gene_dict = link_genes(
        ensembl_lines=transcripts_handle, 
        hgnc_lines=hgnc_handle, 
        exac_lines=exac_handle, 
        hpo_lines=hpo_genes_handle
    )
    
    return gene_dict

@pytest.fixture
def hpo_terms_handle(request, hpo_terms_file):
    """Get a file handle to a hpo terms file"""
    print('')
    return get_file_handle(hpo_terms_file)

@pytest.fixture
def hpo_terms(request, hpo_terms_handle):
    """Get a dictionary with the hpo terms"""
    print('')
    return parse_hpo_phenotypes(hpo_terms_handle)

@pytest.fixture
def hpo_disease_handle(request, hpo_disease_file):
    """Get a file handle to a hpo disease file"""
    print('')
    return get_file_handle(hpo_disease_file)

@pytest.fixture
def hpo_diseases(request, hpo_disease_handle):
    """Get a file handle to a hpo disease file"""
    print('')
    diseases = parse_hpo_diseases(hpo_disease_handle)
    return diseases


##################### Case fixtures #####################

@pytest.fixture(scope='function')
def ped_lines(request, scout_config):
    """Get the lines for a case"""
    case_lines = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "643594	ADM1059A1	0	0	1	1",
        "643594	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
        "643594	ADM1059A3	0	0	2	1",
        ]
    return case_lines


@pytest.fixture(scope='function')
def case_lines(request, scout_config):
    """Get the lines for a case"""
    case = parse_case(scout_config)
    return case


@pytest.fixture(scope='function')
def parsed_case(request, scout_config):
    """Get the lines for a case"""
    case = parse_case(scout_config)
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
def adapter(request, client):
    """Get an adapter connected to mongomock database"""
    mongo_client = client
    
    database = 'test'
    host = 'localhost'
    port = 27017

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
def gene_database(request, adapter, genes):
    "Returns an adapter to a database populated with user, institute and case"
    load_hgnc_genes(adapter, genes)

    return adapter

@pytest.fixture(scope='function')
def panel_database(request, gene_database, panel_info, institute_obj, parsed_user):
    "Returns an adapter to a database populated with user, institute and case"
    mongo_adapter = gene_database
    mongo_adapter.add_institute(institute_obj)
    mongo_adapter.getoradd_user(
        email=parsed_user['email'],
        name=parsed_user['name'],
        location=parsed_user['location'],
        institutes=parsed_user['institutes']
    )
    load_panel(
        adapter=mongo_adapter, 
        panel_info=panel_info
    )
    
    return mongo_adapter


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
    
    # load_hgnc_genes(
    #     adapter=adapter,
    #     ensembl_lines=ensembl_handle,
    #     hgnc_lines=hgnc_handle,
    #     exac_lines=exac_handle,
    #     hpo_lines=hpo_handle
    # )

    return adapter


@pytest.fixture(scope='function')
def variant_database(request, populated_database, variant_objs, sv_variant_objs):
    """Returns an adapter to a database populated with user, institute, case
       and variants"""
    adapter = populated_database
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
            'date': datetime.date.today(),
            'file': panel_1_path,
            'type': 'clinical',
            'institute': 'cust000',
            'version': '1.0',
            'name': 'panel1',
            'full_name': 'Test panel'
        }
    return panel


@pytest.fixture(scope='function')
def parsed_panel(request, panel_info):
    """docstring for parsed_panels"""
    panel = parse_gene_panel(panel_info)

    return panel


@pytest.fixture(scope='function')
def panel_obj(request, parsed_panel, gene_database):
    """docstring for parsed_panels"""
    panel = build_panel(parsed_panel, gene_database)

    return panel


##################### Variant fixtures #####################
@pytest.fixture(scope='function')
def basic_variant_dict(request):
    """Return a variant dict with the required information"""
    variant = {
        'CHROM': '1',
        'ID': '.',
        'POS': '10',
        'REF': 'A',
        'ALT': 'C',
        'QUAL': '100',
        'FILTER': 'PASS',
        'FORMAT': 'GT',
        'INFO': '.',
        'info_dict':{},
    }
    return variant

@pytest.fixture(scope='function')
def one_variant(request, variant_clinical_file):
    logger.info("Return one parsed variant")
    variant_parser = VCFParser(infile=variant_clinical_file)
    
    for variant in variant_parser:
        break
    
    return variant

@pytest.fixture(scope='function')
def one_sv_variant(request, sv_clinical_file):
    logger.info("Return one parsed SV variant")
    variant_parser = VCFParser(infile=sv_clinical_file)

    for variant in variant_parser:
        break

    return variant

@pytest.fixture(scope='function')
def rank_results_header(request, variant_clinical_file):
    logger.info("Return a VCF parser with one variant")
    variant = VCFParser(infile=variant_clinical_file)
    rank_results = []
    for info_line in variant.metadata.info_lines:
        if info_line['ID'] == 'RankResult':
            rank_results = info_line['Description'].split('|')
    
    return rank_results

@pytest.fixture(scope='function')
def sv_variants(request, sv_clinical_file):
    logger.info("Return a VCF parser many svs")
    variants = VCFParser(infile=sv_clinical_file)
    return variants

@pytest.fixture(scope='function')
def variants(request, variant_clinical_file):
    logger.info("Return a VCF parser many svs")
    variants = VCFParser(infile=variant_clinical_file)
    return variants

@pytest.fixture(scope='function')
def parsed_variant(request, one_variant, parsed_case):
    """Return a parsed variant"""
    print('')
    variant_dict = parse_variant(one_variant, parsed_case)
    return variant_dict

@pytest.fixture(scope='function')
def parsed_sv_variant(request, one_sv_variant, parsed_case):
    """Return a parsed variant"""
    print('')
    variant_dict = parse_variant(one_sv_variant, parsed_case)
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
