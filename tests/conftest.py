# -*- coding: utf-8 -*-
import datetime
import logging
import os
from pprint import pprint as pp

import pymongo
import pytest
import yaml
from cyvcf2 import VCF

# Adapter stuff
from mongomock import MongoClient

from scout.adapter.mongo import MongoAdapter as PymongoAdapter
from scout.build import build_case, build_institute, build_panel
from scout.build.genes.hgnc_gene import build_hgnc_gene
from scout.build.genes.transcript import build_transcript
from scout.build.user import build_user
from scout.build.variant import build_variant
from scout.demo import (
    cancer_load_path,
    cancer_sv_path,
    cancer_snv_path,
    clinical_snv_path,
    clinical_str_path,
    clinical_sv_path,
    customannotation_snv_path,
    empty_sv_clinical_path,
    load_path,
    panel_path,
    ped_path,
    research_snv_path,
    research_sv_path,
    vep_97_annotated_path,
)

# These are the reduced data files
from scout.demo.resources import (
    exac_reduced_path,
    exons37_reduced_path,
    exons38_reduced_path,
    genemap2_reduced_path,
    genes37_reduced_path,
    genes38_reduced_path,
    hgnc_reduced_path,
    mim2gene_reduced_path,
    transcripts37_reduced_path,
    transcripts38_reduced_path,
    genes_to_phenotype_reduced_path,
    hpoterms_reduced_path,
    phenotype_to_genes_reduced_path,
)
from scout.load import load_hgnc_genes
from scout.load.hpo import load_hpo
from scout.load.transcript import load_transcripts
from scout.log import init_log
from scout.models.hgnc_map import HgncGene
from scout.parse.case import parse_case
from scout.parse.ensembl import (
    parse_ensembl_exons,
    parse_ensembl_transcripts,
    parse_transcripts,
)
from scout.parse.exac import parse_exac_genes
from scout.parse.hgnc import parse_hgnc_genes
from scout.parse.panel import parse_gene_panel
from scout.parse.variant import parse_variant
from scout.parse.variant.headers import parse_rank_results_header
from scout.server.blueprints.login.models import LoginUser
from scout.server.app import create_app
from scout.utils.handle import get_file_handle
from scout.utils.link import link_genes

DATABASE = "testdb"
REAL_DATABASE = "realtestdb"

# root_logger = logging.getLogger()
# init_log(root_logger, loglevel='INFO')
LOG = logging.getLogger(__name__)


@pytest.fixture
def mock_app(real_populated_database):
    """Return the path to a mocked app object with data"""
    _mock_app = create_app(
        config=dict(
            TESTING=True,
            DEBUG=True,
            MONGO_DBNAME=REAL_DATABASE,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
        )
    )
    return _mock_app


##################### Gene fixtures #####################


@pytest.fixture
def gene_obj():
    """Get a dictionary with with gene obj information"""
    gene = HgncGene(
        hgnc_symbol="B3GALT6",
        hgnc_id=17978,
        ensembl_id="ENSG00000176022",
        chrom="1",
        start=1232237,
        end=1235041,
        build="38",
    )

    return gene


@pytest.fixture
def unparsed_transcript(request):
    """Get a dictionary with *unparsed* transcript information"""
    unparsed_transcript = dict(
        chrom="1",
        end=1170421,
        ens_gene_id="ENSG00000176022",
        ens_transcript_id="ENST00000379198",
        refseq_mrna="NM_080605",
        refseq_mrna_pred="",
        refseq_ncrna="",
        start=1167629,
    )
    return unparsed_transcript


@pytest.fixture
def transcript_info():
    """Get a dictionary with parsed transcript information"""
    transcript = {
        "chrom": "1",
        "ensembl_gene_id": "ENSG00000176022",
        "ensembl_transcript_id": "ENST00000379198",
        "hgnc_id": 17978,
        "mrna": {"NM_080605"},
        "mrna_predicted": set(),
        "nc_rna": set(),
        "primary_transcripts": {"NM_080605"},
        "transcript_end": 1170421,
        "transcript_start": 1167629,
    }
    return transcript


@pytest.fixture
def genes(
    request,
    genes37_handle,
    hgnc_handle,
    exac_handle,
    mim2gene_handle,
    genemap_handle,
    hpo_genes_handle,
):
    """Get a dictionary with the linked genes"""
    print("")

    gene_dict = link_genes(
        ensembl_lines=genes37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
    )

    return gene_dict


@pytest.fixture
def ensembl_genes(request, gene_bulk):
    """Return a dictionary that maps ensembl ids on genes"""
    _ensembl_genes = {}
    for gene_obj in gene_bulk:
        _ensembl_genes[gene_obj["ensembl_id"]] = gene_obj
    return _ensembl_genes


@pytest.fixture(scope="function")
def gene_bulk(genes):
    """Return a list with HgncGene objects"""
    bulk = []
    for gene_key in genes:
        bulk.append(build_hgnc_gene(genes[gene_key]))

    return bulk


@pytest.fixture(scope="function")
def gene_bulk_38(genes):
    """Return a list with HgncGene objects"""
    bulk = []
    for gene_key in genes:
        gene_obj = build_hgnc_gene(genes[gene_key])
        gene_obj["build"] = "38"
        bulk.append(gene_obj)

    return bulk


@pytest.fixture(scope="function")
def gene_bulk_all(gene_bulk, gene_bulk_38):
    """Return a list with HgncGene objects"""

    return gene_bulk + gene_bulk_38


@pytest.fixture
def transcript_objs(request, parsed_transcripts):
    """Return a list with transcript objs"""
    print("")

    _transcripts = []
    for tx_id in parsed_transcripts:
        tx_info = parsed_transcripts[tx_id]
        _transcripts.append(build_transcript(tx_info))

    return _transcripts


#############################################################
################# Hpo terms fixtures ########################
#############################################################


@pytest.fixture
def hpo_genes_handle(request, hpo_genes_file):
    """Get a file handle to a genes_to_phenotypes HPO mapping file"""
    return get_file_handle(hpo_genes_file)


@pytest.fixture
def hpo_genes_file(request):
    """Get the path to the genes_to_phenotypes HPO mapping file"""
    return genes_to_phenotype_reduced_path


@pytest.fixture
def test_hpo_terms(request):
    """Return a list with 3 HPO terms formatted
    as case_obj.phenotyope terms"""
    pheno_terms = [
        {"phenotype_id": "HP:0000533", "feature": "Chorioretinal atrophy"},
        {"phenotype_id": "HP:0000529", "feature": "Progressive visual loss"},
        {"phenotype_id": "HP:0000543", "feature": "Optic disc pallor"},
    ]
    return pheno_terms


@pytest.fixture
def phenotype_to_genes_file(request):
    """Get the path to the phenotypes_to_genes mapping file"""
    return phenotype_to_genes_reduced_path


@pytest.fixture
def hpo_terms_handle(request, hpo_terms_file):
    """Get a file handle to a hpo terms file (http://purl.obolibrary.org/obo/hp.obo)"""
    hpo_lines = get_file_handle(hpo_terms_file)
    return hpo_lines


@pytest.fixture
def hpo_terms_file(request):
    """Get the path to the hpo terms file"""
    return hpoterms_reduced_path


@pytest.fixture
def hpo_disease_handle(request, phenotype_to_genes_file):
    """Get a file handle to a phenotypes_to_genes mapping file"""
    handle = get_file_handle(phenotype_to_genes_file)
    return handle


@pytest.fixture(scope="function")
def hpo_database(
    request,
    gene_database,
    hpo_terms_handle,
    hpo_genes_handle,
    hpo_disease_handle,
    phenotype_to_genes_file,
):
    "Returns an adapter to a database populated with hpo terms"
    adapter = gene_database

    load_hpo(
        adapter=gene_database,
        disease_lines=get_file_handle(genemap2_reduced_path),
        hpo_lines=get_file_handle(hpoterms_reduced_path),
        hpo_gene_lines=get_file_handle(phenotype_to_genes_file),
    )
    return adapter


#############################################################
################# OMIM terms fixtures #######################
#############################################################


@pytest.fixture
def test_omim_term(request):
    """Return a test OMIM object"""

    omim_term = {
        "_id": "OMIM:260005",
        "disease_id": "OMIM:260005",
        "disease_nr": 260005,
        "description": "5-oxoprolinase deficiency",
        "source": "OMIM",
        "genes": [8149],
        "inheritance": ["AR", "AD"],
        "HPO_terms": ["HP:00022027", "HP:0008672"],
    }
    return omim_term


#############################################################
##################### Case fixtures #########################
#############################################################
@pytest.fixture(scope="function")
def ped_lines(request):
    """Get the lines for a case"""
    case_lines = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "643594	ADM1059A1	0	0	1	1",
        "643594	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
        "643594	ADM1059A3	0	0	2	1",
    ]
    return case_lines


@pytest.fixture(scope="function")
def case_lines(request, scout_config):
    """Get the lines for a case"""
    case = parse_case(scout_config)
    return case


@pytest.fixture(scope="function")
def parsed_case(request, scout_config):
    """Get the lines for a case"""
    case = parse_case(scout_config)
    return case


@pytest.fixture(scope="function")
def cancer_parsed_case(request, cancer_scout_config):
    """Get the lines for a cancer case"""
    case = parse_case(cancer_scout_config)
    return case


@pytest.fixture(scope="function")
def cancer_case_obj(request, cancer_parsed_case):
    """Return a cancer case object"""

    case = cancer_parsed_case
    case["_id"] = cancer_parsed_case["case_id"]
    case["owner"] = cancer_parsed_case["owner"]
    case["has_svvariants"] = True

    case["individuals"][0]["sex"] = "1"
    case["individuals"][1]["sex"] = "1"

    return case


@pytest.fixture(scope="function")
def case_obj(request, parsed_case):

    case = parsed_case
    case["_id"] = parsed_case["case_id"]
    case["owner"] = parsed_case["owner"]
    case["created_at"] = parsed_case["analysis_date"]
    case["dynamic_gene_list"] = []
    case["genome_version"] = None
    case["has_svvariants"] = True

    case["individuals"][0]["sex"] = "1"
    case["individuals"][1]["sex"] = "1"
    case["individuals"][2]["sex"] = "2"

    case["is_migrated"] = False
    case["is_research"] = False

    case["panels"] = [
        {
            "display_name": "Test panel",
            "is_default": True,
            "nr_genes": 263,
            "panel_id": "panel1",
            "panel_name": "panel1",
            "updated_at": datetime.datetime(2018, 4, 25, 15, 43, 44, 823465),
            "version": 1.0,
        }
    ]
    case["rerun_requested"] = False
    case["research_requested"] = False
    case["status"] = "inactive"
    case["synopsis"] = ""
    case["updated_at"] = parsed_case["analysis_date"]
    case["delivery_report"] = parsed_case["delivery_report"]
    case["assignees"] = []
    case["phenotype_terms"] = []  # do not assign any phenotype
    case["cohorts"] = []  # do not assign any cohort

    return case


#############################################################
##################### Clinvar fixtures ######################
#############################################################
@pytest.fixture(scope="function")
def clinvar_variant(request):

    variant = {
        "_id": "internal_id_4c7d5c70d955875504db72ef8e1abe77",
        "csv_type": "variant",
        "case_id": "internal_id",
        "category": "snv",
        "local_id": "4c7d5c70d955875504db72ef8e1abe77",
        "linking_id": "4c7d5c70d955875504db72ef8e1abe77",
        "gene_symbol": "POT1",
        "ref_seq": "NM_001042594.1",
        "hgvs": "c.510G>T",
        "chromosome": "7",
        "start": "124491972",
        "stop": "124491972",
        "ref": "C",
        "alt": "A",
        "variations_ids": "rs116916706",
        "clinsig": "Pathogenic",
        "last_evaluated": "2020-06-09",
        "assertion_method": "ACMG Guidelines, 2015",
        "assertion_method_cit": "PMID:25741868",
        "inheritance_mode": "Autosomal recessive inheritance",
    }
    return variant


@pytest.fixture(scope="function")
def clinvar_casedata(request):

    casedata = {
        "_id": "internal_id_4c7d5c70d955875504db72ef8e1abe77_NA12882",
        "csv_type": "casedata",
        "case_id": "internal_id",
        "category": "snv",
        "linking_id": "4c7d5c70d955875504db72ef8e1abe77",
        "individual_id": "NA12882",
        "collection_method": "clinical testing",
        "allele_origin": "germline",
        "is_affected": "yes",
        "sex": "male",
        "fam_history": "no",
        "is_proband": "yes",
        "is_secondary_finding": "no",
        "is_mosaic": "no",
        "zygosity": "compound heterozygote",
        "platform_type": "next-gen sequencing",
        "platform_name": "Whole exome sequencing, Illumina",
        "method_purpose": "discovery",
        "reported_at": "2016-10-12",
    }

    return casedata


#############################################################
##################### Institute fixtures ####################
#############################################################
@pytest.fixture(scope="function")
def parsed_institute(request):
    print("")
    institute = {
        "institute_id": "cust000",
        "display_name": "test_institute",
        "sanger_recipients": ["john@doe.com", "jane@doe.com"],
    }

    return institute


@pytest.fixture(scope="function")
def institute_obj(request, parsed_institute):
    print("")
    LOG.info("Building a institute")
    institute = build_institute(
        internal_id=parsed_institute["institute_id"],
        display_name=parsed_institute["display_name"],
        sanger_recipients=parsed_institute["sanger_recipients"],
    )
    # move institute created time 1 day back in time
    institute["created_at"] = datetime.datetime.now() - datetime.timedelta(days=1)
    return institute


#############################################################
################# Managed variant fixtures ##################
#############################################################


@pytest.fixture(scope="function")
def managed_variants_lines(request):
    managed_variants_lines = [
        "##my_csv_file",
        "#chromosome;position;end;reference;alternative;category;sub_category;description\n",
        "14;76548781;76548781;CTGGACC;G;snv;indel;IFT43 indel test\n",
        "17;48696925;48696925;G;T;snv;snv;CACNA1G intronic test\n",
        "7;124491972;124491972;C;A;snv;snv;POT1 test snv\n",
    ]
    return managed_variants_lines


@pytest.fixture(scope="function")
def managed_variants_first_line_header(request):
    managed_variants_lines = [
        "chromosome;position;end;reference;alternative;category;sub_category;description\n",
        "14;76548781;76548781;CTGGACC;G;snv;indel;IFT43 indel test\n",
        "17;48696925;48696925;G;T;snv;snv;CACNA1G intronic test\n",
        ";;;;;;;\n",
        "7;124491972;124491972;C;A;snv;snv;POT1 test snv\n",
    ]
    return managed_variants_lines


#############################################################
##################### User fixtures #########################
#############################################################
@pytest.fixture(scope="function")
def parsed_user(request, institute_obj):
    """Return user info"""
    user_info = {
        "email": "john@doe.com",
        "name": "John Doe",
        "location": "here",
        "institutes": [institute_obj["internal_id"]],
        "roles": ["admin"],
    }
    return user_info


@pytest.fixture(scope="function")
def user_obj(request, parsed_user):
    """Return a User object"""
    _user_obj = build_user(parsed_user)
    return _user_obj


#############################################################
##################### Adapter fixtures #####################
#############################################################

# We need to monkeypatch 'connect' function so the tests use a mongomock database
# @pytest.fixture(autouse=True)
# def no_connect(monkeypatch):
#     # from scout.adapter.client import get_connection
#     mongo = Mock(return_value=MongoClient())
#     print('hej')
#
#     monkeypatch.setattr('scout.adapter.client.get_connection', mongo)


@pytest.fixture(scope="function")
def database_name(request):
    """Get the name of the test database"""
    return DATABASE


@pytest.fixture(scope="function")
def real_database_name(request):
    """Get the name of the test database"""
    return REAL_DATABASE


@pytest.fixture(scope="function")
def pymongo_client(request):
    """Get a client to the mongo database"""

    LOG.info("Get a mongomock client")
    start_time = datetime.datetime.now()
    mock_client = MongoClient()

    def teardown():
        print("\n")
        LOG.info("Deleting database")
        mock_client.drop_database(DATABASE)
        LOG.info("Database deleted")
        LOG.info("Time to run test:{}".format(datetime.datetime.now() - start_time))

    request.addfinalizer(teardown)

    return mock_client


@pytest.fixture(scope="function")
def real_pymongo_client(request):
    """Get a client to the mongo database"""

    LOG.info("Get a real pymongo client")
    start_time = datetime.datetime.now()
    mongo_client = pymongo.MongoClient()

    def teardown():
        print("\n")
        LOG.info("Deleting database")
        mongo_client.drop_database(REAL_DATABASE)
        LOG.info("Database deleted")
        LOG.info("Time to run test:{}".format(datetime.datetime.now() - start_time))

    request.addfinalizer(teardown)

    return mongo_client


@pytest.fixture(scope="function")
def real_adapter(request, real_pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = real_pymongo_client

    LOG.info("Connecting to database %s", REAL_DATABASE)

    database = mongo_client[REAL_DATABASE]
    mongo_adapter = PymongoAdapter(database)

    mongo_adapter.load_indexes()

    LOG.info("Connected to database")

    return mongo_adapter


@pytest.fixture(scope="function")
def adapter(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    LOG.info("Connecting to database...")
    mongo_client = pymongo_client

    database = mongo_client[DATABASE]
    mongo_adapter = PymongoAdapter(database)
    mongo_adapter.setup(database)

    LOG.info("Connected to database")

    return mongo_adapter


@pytest.fixture(scope="function")
def institute_database(request, adapter, institute_obj, user_obj):
    "Returns an adapter to a database populated with institute"
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    return adapter


@pytest.fixture(scope="function")
def real_institute_database(request, real_adapter, institute_obj, user_obj):
    "Returns an adapter to a database populated with institute"
    adapter = real_adapter
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    return adapter


@pytest.fixture(scope="function")
def gene_database(request, institute_database, genes):
    "Returns an adapter to a database populated with user, institute, case and genes"
    adapter = institute_database

    gene_objs = load_hgnc_genes(adapter=adapter, genes=genes, build="37")

    LOG.info("Creating index on hgnc collection")
    adapter.hgnc_collection.create_index(
        [("build", pymongo.ASCENDING), ("hgnc_symbol", pymongo.ASCENDING)]
    )

    transcripts_handle = get_file_handle(transcripts37_reduced_path)
    load_transcripts(adapter, transcripts_handle, build="37")

    adapter.transcript_collection.create_index(
        [("build", pymongo.ASCENDING), ("hgnc_id", pymongo.ASCENDING)]
    )

    LOG.info("Index done")

    return adapter


@pytest.fixture(scope="function")
def real_gene_database(
    request,
    real_institute_database,
    genes37_handle,
    hgnc_handle,
    exac_handle,
    mim2gene_handle,
    genemap_handle,
    hpo_genes_handle,
):
    "Returns an adapter to a database populated with user, institute, case and genes"
    adapter = real_institute_database

    load_hgnc_genes(
        adapter=adapter,
        ensembl_lines=genes37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
        build="37",
    )

    LOG.info("Creating index on hgnc collection")
    adapter.hgnc_collection.create_index(
        [("build", pymongo.ASCENDING), ("hgnc_symbol", pymongo.ASCENDING)]
    )
    LOG.info("Index done")

    return adapter


@pytest.fixture(scope="function")
def panel_database(request, gene_database, parsed_panel):
    "Returns an adapter to a database populated with user, institute and case"
    adapter = gene_database
    LOG.info("Adding panel to adapter")

    adapter.load_panel(parsed_panel=parsed_panel)

    return adapter


@pytest.fixture(scope="function")
def real_panel_database(request, real_gene_database, parsed_panel):
    "Returns an adapter to a database populated with user, institute and case"
    adapter = real_gene_database
    LOG.info("Adding panel to real adapter")

    adapter.load_panel(parsed_panel=parsed_panel)

    return adapter


@pytest.fixture(scope="function")
def case_database(request, panel_database, parsed_case):
    "Returns an adapter to a database populated with institute, user and case"
    adapter = panel_database
    case_obj = build_case(parsed_case, adapter)
    adapter._add_case(case_obj)

    return adapter


@pytest.fixture(scope="function")
def populated_database(request, panel_database, parsed_case):
    "Returns an adapter to a database populated with user, institute case, genes, panels"
    adapter = panel_database

    LOG.info("Adding case to adapter")
    case_obj = build_case(parsed_case, adapter)
    adapter._add_case(case_obj)
    return adapter


@pytest.fixture(scope="function")
def real_populated_database(request, real_panel_database, parsed_case):
    "Returns an adapter to a database populated with user, institute case, genes, panels"
    adapter = real_panel_database

    LOG.info("Adding case to real adapter")
    case_obj = build_case(parsed_case, adapter)
    adapter._add_case(case_obj)

    return adapter


@pytest.fixture(scope="function")
def variant_database(request, populated_database):
    """Returns an adapter to a database populated with user, institute, case
    and variants"""
    adapter = populated_database
    # Load variants
    case_obj = adapter.case_collection.find_one()

    adapter.load_variants(
        case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=-10,
        build="37",
    )

    return adapter


@pytest.fixture(scope="function")
def real_variant_database(request, real_populated_database):
    """Returns an adapter to a database populated with user, institute, case
    and variants"""
    adapter = real_populated_database

    case_obj = adapter.case_collection.find_one()
    # Load variants
    adapter.load_variants(
        case_obj,
        variant_type="clinical",
        category="snv",
        rank_threshold=-10,
        build="37",
    )

    return adapter


@pytest.fixture(scope="function")
def sv_database(request, populated_database, variant_objs, sv_variant_objs):
    """Returns an adapter to a database populated with user, institute, case
    and variants"""
    adapter = populated_database

    case_obj = adapter.case_collection.find_one()
    # Load sv variants
    adapter.load_variants(
        case_obj, variant_type="clinical", category="sv", rank_threshold=-10, build="37"
    )

    return adapter


#############################################################
##################### Panel fixtures #####################
#############################################################
@pytest.fixture(scope="function")
def panel_info(request):
    "Return one panel info as specified in tests/fixtures/config1.ini"
    panel = {
        "date": datetime.datetime.now(),
        "file": panel_path,
        "type": "clinical",
        "institute": "cust000",
        "version": "1.0",
        "panel_name": "panel1",
        "full_name": "Test panel",
    }
    return panel


@pytest.fixture(scope="function")
def parsed_panel(request, panel_info):
    """docstring for parsed_panels"""
    panel = parse_gene_panel(
        path=panel_info["file"],
        institute=panel_info["institute"],
        panel_id=panel_info["panel_name"],
        panel_type=panel_info["type"],
        date=panel_info["date"],
        version=panel_info["version"],
        display_name=panel_info["full_name"],
    )

    return panel


@pytest.fixture(scope="function")
def dummypanel_geneobj():
    """A panel gene object"""
    gene_obj = {}

    gene_obj["symbol"] = "AAA"
    gene_obj["hgnc_id"] = 100

    return gene_obj


@pytest.fixture(scope="function")
def dummypanel_obj(parsed_panel, dummypanel_geneobj):
    """Return a dummy panel object"""
    dummy_panel = {}

    dummy_panel["panel_name"] = parsed_panel["panel_id"]
    dummy_panel["institute"] = parsed_panel["institute"]
    dummy_panel["version"] = float(parsed_panel["version"])
    dummy_panel["date"] = parsed_panel["date"]
    dummy_panel["display_name"] = parsed_panel["display_name"]
    dummy_panel["description"] = "A panel description"
    dummy_panel["genes"] = [
        {"symbol": "AAA", "hgnc_id": 100},
        {"symbol": "BBB", "hgnc_id": 222},
    ]

    return dummy_panel


@pytest.fixture(scope="function")
def panel_obj(request, parsed_panel, gene_database):
    """Return a panel object"""
    panel = build_panel(parsed_panel, gene_database)

    return panel


@pytest.fixture(scope="function")
def gene_panels(request, parsed_case):
    """Return a list with the gene panels of parsed case"""
    panels = parsed_case["gene_panels"]

    return panels


@pytest.fixture(scope="function")
def default_panels(request, parsed_case):
    """Return a list with the gene panels of parsed case"""
    panels = parsed_case["default_panels"]

    return panels


#############################################################
##################### Variant fixtures #####################
#############################################################
@pytest.fixture(scope="function")
def basic_variant_dict(request):
    """Return a variant dict with the required information"""
    variant = {
        "CHROM": "1",
        "ID": ".",
        "POS": "10",
        "REF": "A",
        "ALT": "C",
        "QUAL": "100",
        "FILTER": "PASS",
        "FORMAT": "GT",
        "INFO": ".",
        "info_dict": {},
    }
    return variant


@pytest.fixture(scope="function")
def one_variant(request, variant_clinical_file):
    LOG.info("Return one parsed variant")
    variant_parser = VCF(variant_clinical_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def one_vep97_annotated_variant(request, vep_97_annotated_variant_clinical_file):
    LOG.info("Return one parsed variant")
    variant_parser = VCF(vep_97_annotated_variant_clinical_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def one_cancer_manta_SV_variant(request, vep_94_manta_annotated_SV_variants_file):
    LOG.info("Return one parsed cancer SV variant")
    variant_parser = VCF(vep_94_manta_annotated_SV_variants_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def one_cancer_variant(request, cancer_snv_file):
    LOG.info("Return one parsed cancer variant")
    variant_parser = VCF(cancer_snv_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def parsed_cancer_variant(request, one_cancer_variant, cancer_case_obj):
    """Return a parsed variant"""
    variant_dict = parse_variant(one_cancer_variant, cancer_case_obj)
    return variant_dict


@pytest.fixture(scope="function")
def cancer_variant_obj(request, parsed_cancer_variant):
    LOG.info("Return one cancer variant obj")
    institute_id = "cust000"

    variant = build_variant(parsed_cancer_variant, institute_id=institute_id)
    return variant


@pytest.fixture(scope="function")
def one_variant_customannotation(request, customannotation_snv_file):
    LOG.info("Return one parsed variant with custom annotations")
    variant_parser = VCF(customannotation_snv_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def one_sv_variant(request, sv_clinical_file):
    LOG.info("Return one parsed SV variant")
    variant_parser = VCF(sv_clinical_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def one_str_variant(request, str_clinical_file):
    LOG.info("Return one parsed STR variant")
    variant_parser = VCF(str_clinical_file)

    variant = next(variant_parser)
    return variant


@pytest.fixture(scope="function")
def rank_results_header(request, variant_clinical_file):
    LOG.info("Return a VCF parser with one variant")
    variants = VCF(variant_clinical_file)
    rank_results = parse_rank_results_header(variants)

    return rank_results


@pytest.fixture(scope="function")
def sv_variants(request, sv_clinical_file):
    LOG.info("Return a VCF parser many svs")
    variants = VCF(sv_clinical_file)
    return variants


@pytest.fixture(scope="function")
def str_variants(request, str_clinical_file):
    LOG.info("Return a VCF parser many STRs")
    variants = VCF(str_clinical_file)
    return variants


@pytest.fixture(scope="function")
def variants(request, variant_clinical_file):
    LOG.info("Return a VCF parser many svs")
    variants = VCF(variant_clinical_file)
    return variants


@pytest.fixture(scope="function")
def parsed_variant(request, one_variant, case_obj):
    """Return a parsed variant"""
    print("")
    variant_dict = parse_variant(one_variant, case_obj)
    return variant_dict


@pytest.fixture(scope="function")
def parsed_str_variant(request, one_str_variant, case_obj):
    """Return a parsed variant"""
    print("")
    variant_dict = parse_variant(one_str_variant, case_obj)
    return variant_dict


@pytest.fixture(scope="function")
def variant_obj(request, parsed_variant):
    """Return a variant object"""
    print("")
    institute_id = "cust000"
    variant = build_variant(parsed_variant, institute_id=institute_id)
    return variant


@pytest.fixture(scope="function")
def str_variant_obj(request, parsed_str_variant):
    """Return a variant object"""
    print("")
    institute_id = "cust000"
    variant = build_variant(parsed_str_variant, institute_id=institute_id)
    return variant


@pytest.fixture(scope="function")
def cyvcf2_variant():
    """Return a variant object"""

    class Cyvcf2Variant(object):
        def __init__(self):
            self.CHROM = "1"
            self.REF = "A"
            self.ALT = ["C"]
            self.POS = 10
            self.end = 11
            self.FILTER = None
            self.ID = "."
            self.QUAL = None
            self.var_type = "snp"
            self.INFO = {"RankScore": "internal_id:10"}

    variant = Cyvcf2Variant()
    return variant


# @pytest.fixture(scope='function')
# def parsed_variant():
#     """Return variant information for a parsed variant with minimal information"""
#     variant = {'alternative': 'C',
#                'callers': {
#                    'freebayes': None,
#                    'gatk': None,
#                    'samtools': None
#                },
#                'case_id': 'cust000-643594',
#                'category': 'snv',
#                'chromosome': '2',
#                'clnsig': [],
#                'compounds': [],
#                'conservation': {'gerp': [], 'phast': [], 'phylop': []},
#                'dbsnp_id': None,
#                'end': 176968945,
#                'filters': ['PASS'],
#                'frequencies': {
#                    'exac': None,
#                    'exac_max': None,
#                    'thousand_g': None,
#                    'thousand_g_left': None,
#                    'thousand_g_max': None,
#                    'thousand_g_right': None},
#                'genes': [],
#                'genetic_models': [],
#                'hgnc_ids': [],
#                'ids': {'display_name': '1_10_A_C_clinical',
#                        'document_id': 'a1f1d2ac588dae7883f474d41cfb34b8',
#                        'simple_id': '1_10_A_C',
#                        'variant_id': 'e8e33544a4745f8f5a09c5dea3b0dbe4'},
#                'length': 1,
#                'local_obs_hom_old': None,
#                'local_obs_old': None,
#                'mate_id': None,
#                'position': 176968944,
#                'quality': 10.0,
#                'rank_score': 0.0,
#                'reference': 'A',
#                'samples': [{'alt_depth': -1,
#                             'display_name': 'NA12882',
#                             'genotype_call': None,
#                             'genotype_quality': None,
#                             'individual_id': 'ADM1059A2',
#                             'read_depth': None,
#                             'ref_depth': -1},
#                            {'alt_depth': -1,
#                             'display_name': 'NA12877',
#                             'genotype_call': None,
#                             'genotype_quality': None,
#                             'individual_id': 'ADM1059A1',
#                             'read_depth': None,
#                             'ref_depth': -1},
#                            {'alt_depth': -1,
#                             'display_name': 'NA12878',
#                             'genotype_call': None,
#                             'genotype_quality': None,
#                             'individual_id': 'ADM1059A3',
#                             'read_depth': None,
#                             'ref_depth': -1}],
#                'sub_category': 'snv',
#                'variant_type': 'clinical'}
#     return variant


@pytest.fixture(scope="function")
def parsed_sv_variant(request, one_sv_variant, case_obj):
    """Return a parsed variant"""
    print("")
    variant_dict = parse_variant(one_sv_variant, case_obj)
    return variant_dict


@pytest.fixture(scope="function")
def parsed_variants(request, variants, case_obj):
    """Get a generator with parsed variants"""
    print("")
    individual_positions = {}
    for i, ind in enumerate(variants.samples):
        individual_positions[ind] = i

    return (
        parse_variant(variant, case_obj, individual_positions=individual_positions)
        for variant in variants
    )


@pytest.fixture(scope="function")
def parsed_sv_variants(request, sv_variants, case_obj):
    """Get a generator with parsed variants"""
    print("")
    individual_positions = {}
    for i, ind in enumerate(sv_variants.samples):
        individual_positions[ind] = i

    return (
        parse_variant(variant, case_obj, individual_positions=individual_positions)
        for variant in sv_variants
    )


@pytest.fixture(scope="function")
def variant_objs(request, parsed_variants, institute_obj):
    """Get a generator with parsed variants"""
    print("")
    return (build_variant(variant, institute_obj) for variant in parsed_variants)


@pytest.fixture(scope="function")
def sv_variant_objs(request, parsed_sv_variants, institute_obj):
    """Get a generator with parsed variants"""
    print("")
    return (build_variant(variant, institute_obj) for variant in parsed_sv_variants)


#############################################################
##################### File fixtures #####################
#############################################################


@pytest.fixture
def config_file(request):
    """Get the path to a config file"""
    print("")
    return load_path


@pytest.fixture
def panel_1_file(request):
    """Get the path to a config file"""
    print("")
    return panel_path


@pytest.fixture
def hgnc_file(request):
    """Get the path to a hgnc file"""
    print("")
    return hgnc_reduced_path


@pytest.fixture
def transcripts_file(request):
    """Get the path to a ensembl transcripts file"""
    print("")
    return transcripts37_reduced_path


@pytest.fixture
def exons_file(request):
    """Get the path to a ensembl exons file"""
    print("")
    return exons37_reduced_path


@pytest.fixture
def exons_38_file(request):
    """Get the path to a ensembl exons file build 38"""
    print("")
    return exons38_reduced_path


@pytest.fixture
def genes37_file(request):
    """Get the path to a ensembl genes file"""
    print("")
    return genes37_reduced_path


@pytest.fixture
def exac_file(request):
    """Get the path to a exac genes file"""
    print("")
    return exac_reduced_path


@pytest.fixture
def mim2gene_file(request):
    """Get the path to the mim2genes file"""
    print("")
    return mim2gene_reduced_path


@pytest.fixture
def genemap_file(request):
    """Get the path to the mim2genes file"""
    print("")
    return genemap2_reduced_path


@pytest.fixture(scope="function")
def variant_clinical_file(request):
    """Get the path to a variant file"""
    print("")
    return clinical_snv_path


@pytest.fixture(scope="function")
def vep_97_annotated_variant_clinical_file(request):
    """Get a path to a VCF file annotated with VEP and containing conservation
    and REVEL score in the CSQ field
    """
    return vep_97_annotated_path


@pytest.fixture(scope="function")
def vep_94_manta_annotated_SV_variants_file(request):
    """Get a path to a Manta VCF outfile annotated containg SVs
    annotated with VEP
    """
    return cancer_sv_path


@pytest.fixture(scope="function")
def cancer_snv_file(request):
    """Get the path to a variant file"""
    print("")
    return cancer_snv_path


@pytest.fixture(scope="function")
def sv_clinical_file(request):
    """Get the path to a variant file"""
    print("")
    return clinical_sv_path


@pytest.fixture(scope="function")
def str_clinical_file(request):
    """Get the path to a variant file"""
    print("")
    return clinical_str_path


@pytest.fixture(scope="function")
def empty_sv_clinical_file(request):
    """Get the path to a variant file without variants"""
    print("")
    return empty_sv_clinical_path


@pytest.fixture(scope="function")
def customannotation_snv_file(request):
    """Get the path to a variant file with custom annotations"""
    print("")
    return customannotation_snv_path


@pytest.fixture(scope="function")
def ped_file(request):
    """Get the path to a ped file"""
    print("")
    return ped_path


@pytest.fixture(scope="function")
def scout_config(request, config_file):
    """Return a dictionary with scout configs"""
    print("")
    in_handle = get_file_handle(config_file)
    data = yaml.safe_load(in_handle)
    return data


@pytest.fixture(scope="function")
def cancer_scout_config(request):
    """Return a dictionary with cancer case scout configs"""
    in_handle = get_file_handle(cancer_load_path)
    data = yaml.safe_load(in_handle)
    return data


@pytest.fixture(scope="function")
def minimal_config(request, scout_config):
    """Return a minimal config"""
    config = scout_config
    config.pop("madeline")
    config.pop("vcf_sv")
    config.pop("vcf_snv_research")
    config.pop("vcf_sv_research")
    config.pop("gene_panels")
    config.pop("default_gene_panels")
    config.pop("rank_model_version")
    config.pop("rank_score_threshold")
    config.pop("sv_rank_model_version")
    config.pop("human_genome_build")

    return config


@pytest.fixture
def panel_handle(request, panel_1_file):
    """Get a file handle to a gene panel file"""
    print("")
    return get_file_handle(panel_1_file)


@pytest.fixture
def hgnc_handle(request, hgnc_file):
    """Get a file handle to a hgnc file"""
    print("")
    return get_file_handle(hgnc_file)


@pytest.fixture
def hgnc_genes(request, hgnc_handle):
    """Get a dictionary with hgnc genes"""
    print("")
    return parse_hgnc_genes(hgnc_handle)


@pytest.fixture
def genes37_handle(request, genes37_file):
    """Get a file handle to a ensembl gene file"""
    print("")
    return get_file_handle(genes37_file)


@pytest.fixture
def transcripts_handle(request, transcripts_file):
    """Get a file handle to a ensembl transcripts file"""
    print("")
    return get_file_handle(transcripts_file)


@pytest.fixture
def transcripts(request, transcripts_handle):
    """Get the parsed ensembl transcripts"""
    print("")
    return parse_ensembl_transcripts(transcripts_handle)


@pytest.fixture
def exons_handle(request, exons_file):
    """Get a file handle to a ensembl exons file"""
    print("")
    return get_file_handle(exons_file)


@pytest.fixture
def exons_38_handle(request, exons_38_file):
    """Get a file handle to a ensembl exons file"""
    print("")
    return get_file_handle(exons_38_file)


@pytest.fixture
def exons(request, exons_handle):
    """Get the parsed ensembl transcripts"""
    print("")
    return parse_ensembl_exons(exons_handle)


@pytest.fixture
def exons_38(request, exons_38_handle):
    """Get the parsed ensembl transcripts"""
    print("")
    return parse_ensembl_exons(exons_38_handle)


@pytest.fixture
def parsed_transcripts(request, transcripts_handle, ensembl_genes):
    """Get the parsed ensembl transcripts"""
    print("")
    transcripts = parse_transcripts(transcripts_handle)
    for tx_id in transcripts:
        tx_info = transcripts[tx_id]
        ens_gene_id = tx_info["ensembl_gene_id"]
        gene_obj = ensembl_genes.get(ens_gene_id)
        if not gene_obj:
            continue
        tx_info["hgnc_id"] = gene_obj["hgnc_id"]
        tx_info["primary_transcripts"] = set(gene_obj.get("primary_transcripts", []))

    return transcripts


@pytest.fixture
def exac_handle(request, exac_file):
    """Get a file handle to a ensembl gene file"""

    return get_file_handle(exac_file)


@pytest.fixture
def exac_genes(request, exac_handle):
    """Get the parsed exac genes"""

    return parse_exac_genes(exac_handle)


@pytest.fixture
def mim2gene_handle(request, mim2gene_file):
    """Get a file handle to a mim2genes file"""

    return get_file_handle(mim2gene_file)


@pytest.fixture
def genemap_handle(request, genemap_file):
    """Get a file handle to a mim2genes file"""

    return get_file_handle(genemap_file)


#############################################################
###################### Beacon Fixtures ######################
#############################################################


@pytest.fixture(scope="function")
def mocked_beacon():
    """A success response from a mocked Beacon server"""

    class MockBeaconResponse:
        def __init__(self):
            self.status_code = 200
            self.url = "http://beacon_url"
            self.token = "xyz"

        def json(self):
            return {"message": "OK"}

    resp = MockBeaconResponse()
    return resp


#############################################################
#################### MatchMaker Fixtures ####################
#############################################################


@pytest.fixture(scope="function")
def mme_submission():
    mme_subm_obj = {
        "patients": [{"id": "internal_id.ADM1059A2"}],
        "created_at": datetime.datetime(2018, 4, 25, 15, 43, 44, 823465),
        "updated_at": datetime.datetime(2018, 4, 25, 15, 43, 44, 823465),
        "sex": True,
        "features": [],
        "disorders": [],
        "genes_only": False,
    }
    return mme_subm_obj


@pytest.fixture(scope="function")
def mme_patient():
    json_patient = {
        "contact": {
            "href": "mailto:contact_email@email.com",
            "name": "A contact at an institute",
        },
        "features": [{"id": "HP:0001644", "label": "Dilated cardiomyopathy", "observed": "yes"}],
        "genomicFeatures": [
            {
                "gene": {"id": "LIMS2"},
                "type": {"id": "SO:0001583", "label": "MISSENSE"},
                "variant": {
                    "alternateBases": "C",
                    "assembly": "GRCh37",
                    "end": 128412081,
                    "referenceBases": "G",
                    "referenceName": "2",
                    "start": 128412080,
                },
                "zygosity": 1,
            }
        ],
        "id": "internal_id.ADM1059A2",
        "label": "A patient for testing",
    }


@pytest.fixture(scope="function")
def match_objs():
    """Mock the results of an internal and an external match"""
    matches = [
        {  # External match where test_patient is the query and with results
            "_id": {"$oid": "match_1"},
            "created": {"$date": 1549964103911},
            "has_matches": True,
            "data": {
                "patient": {
                    "id": "internal_id.ADM1059A2",
                    "contact": {"href": "mailto:test_contact@email.com"},
                }
            },
            "results": [
                {
                    "node": "external_test_node",
                    "patients": [
                        {
                            "patient": {"id": "match_1_id"},
                            "contact": {
                                "href": "mailto:match_user@mail.com",
                                "name": "Test External User",
                            },
                            "score": {"patient": 0.425},
                        },
                        {
                            "patient": {"id": "match_2_id"},
                            "contact": {
                                "href": "mailto:match_user@mail.com",
                                "name": "Test External User",
                            },
                            "score": {"patient": 0.333},
                        },
                    ],
                }
            ],
            "match_type": "external",
        },
        {  #  Internal match where test_patient is among results
            "_id": {"$oid": "match_2"},
            "created": {"$date": 1549964103911},
            "has_matches": True,
            "data": {
                "patient": {
                    "id": "external_patient_x",
                    "contact": {"href": "mailto:test_contact@email.com"},
                }
            },
            "results": [
                {
                    "node": "internal_node",
                    "patients": [
                        {
                            "patient": {"id": "internal_id.ADM1059A2"},
                            "contact": {
                                "href": "mailto:match_user@mail.com",
                                "name": "Test Internal User",
                            },
                            "score": {"patient": 0.87},
                        },
                        {
                            "patient": {"id": "external_patient_y"},
                            "contact": {
                                "href": "mailto:match_user@mail.com",
                                "name": "Test Internal User",
                            },
                            "score": {"patient": 0.76},
                        },
                    ],
                }
            ],
            "match_type": "internal",
        },
    ]
    return matches
