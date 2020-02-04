# -*- coding: utf-8 -*-
import logging

import pytest
import pymongo

from flask import request
from flask_login import login_user, logout_user

from scout.server.blueprints.login.models import LoginUser
from scout.server.app import create_app
from scout.adapter import MongoAdapter
from scout.load.hgnc_gene import load_hgnc_genes
from scout.load.hpo import load_hpo

log = logging.getLogger(__name__)


class LoqusdbMock:
    """Mock the loqusdb api"""

    def __init__(self):
        self.nr_cases = 130
        self.variants = {"1_169898014_T_C": {"families": ["vitalmouse"]}}

    def case_count(self):
        return self.nr_cases

    def get_variant(self, var_dict):
        var = self.variants.get(var_dict["_id"], {})
        var["total"] = self.nr_cases
        return var

    def _add_variant(self, var_obj):
        simple_id = var_obj["simple_id"]
        case_id = var_obj["case_id"]
        self.variants[simple_id] = {"families": [case_id]}

    def _all_variants(self):
        return self.variants


# -*- coding: utf-8 -*-


class MockMail:
    _send_was_called = False
    _message = None

    def send(self, message):
        self._send_was_called = True
        self._message = message


@pytest.fixture
def mock_mail():
    return MockMail()


@pytest.fixture
def mock_sender():
    return "mock_sender"


@pytest.fixture
def mock_comment():
    return "mock_comment"


@pytest.fixture
def loqusdb():
    """Return a loqusdb mock"""
    loqus_mock = LoqusdbMock()
    return loqus_mock


@pytest.fixture
def app(real_database_name, real_variant_database, user_obj):

    app = create_app(
        config=dict(
            TESTING=True,
            DEBUG=True,
            MONGO_DBNAME=real_database_name,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
        )
    )

    @app.route("/auto_login")
    def auto_login():
        log.debug("Got request for auto login for {}".format(user_obj))
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    return app


@pytest.fixture
def minimal_app(real_database_name, real_populated_database, user_obj):
    "An app without data"
    app = create_app(
        config=dict(
            TESTING=True,
            DEBUG=True,
            MONGO_DBNAME=real_database_name,
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
        )
    )

    @app.route("/auto_login")
    def auto_login():
        log.debug("Got request for auto login for {}".format(user_obj))
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    return app


@pytest.fixture
def institute_info():
    _institute_info = dict(internal_id="cust000", display_name="test_institute")
    return _institute_info


@pytest.fixture
def user_info(institute_info):
    _user_info = dict(
        email="john@doe.com",
        name="John Doe",
        roles=["admin", "mme_submitter"],
        institutes=[institute_info["internal_id"]],
    )
    return _user_info


@pytest.fixture
def ldap_app(request):
    """app ficture for testing LDAP connections."""
    config = {
        "TESTING": True,
        "DEBUG": True,
        "SERVER_NAME": "fakey.server.name",
        "LDAP_HOST": "ldap://test_ldap_server",
        "WTF_CSRF_ENABLED": False,
        "MONGO_DBNAME": "testdb",
    }
    app = create_app(config=config)
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def variant_gene():
    """Returns a dictionary with the information from a variant gene"""
    gene = {
        "hgnc_id": 10729,
        "hgnc_symbol": "SEMA4A",
        "ensembl_id": "ENSG00000196189",
        "description": "semaphorin 4A",
        "inheritance": [],
        "transcripts": [
            {
                "transcript_id": "ENST00000355014",
                "hgnc_id": 10729,
                "protein_id": "ENSP00000347117",
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "Q9H3S1",
                "biotype": "protein_coding",
                "functional_annotations": ["intron_variant"],
                "region_annotations": ["intronic"],
                "intron": "10/14",
                "strand": "+",
                "coding_sequence_name": "c.1135-4554G>A",
                "is_canonical": False,
            },
            {
                "transcript_id": "ENST00000368282",
                "hgnc_id": 10729,
                "protein_id": "ENSP00000357265",
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "Q9H3S1",
                "biotype": "protein_coding",
                "functional_annotations": ["intron_variant"],
                "region_annotations": ["intronic"],
                "intron": "9/13",
                "strand": "+",
                "coding_sequence_name": "c.1135-4554G>A",
                "is_canonical": False,
            },
            {
                "transcript_id": "ENST00000368284",
                "hgnc_id": 10729,
                "protein_id": "ENSP00000357267",
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "Q9H3S1",
                "biotype": "protein_coding",
                "functional_annotations": ["intron_variant"],
                "region_annotations": ["intronic"],
                "intron": "8/12",
                "strand": "+",
                "coding_sequence_name": "c.739-4554G>A",
                "is_canonical": False,
            },
            {
                "transcript_id": "ENST00000368285",
                "hgnc_id": 10729,
                "protein_id": "ENSP00000357268",
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "Q9H3S1",
                "biotype": "protein_coding",
                "functional_annotations": ["intron_variant"],
                "region_annotations": ["intronic"],
                "intron": "10/14",
                "strand": "+",
                "coding_sequence_name": "c.1135-4554G>A",
                "is_canonical": True,
            },
            {
                "transcript_id": "ENST00000368286",
                "hgnc_id": 10729,
                "protein_id": "ENSP00000357269",
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "Q9H3S1",
                "biotype": "protein_coding",
                "functional_annotations": ["intron_variant"],
                "region_annotations": ["intronic"],
                "intron": "9/13",
                "strand": "+",
                "coding_sequence_name": "c.739-4554G>A",
                "is_canonical": False,
            },
            {
                "transcript_id": "ENST00000462892",
                "hgnc_id": 10729,
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "unknown",
                "biotype": "retained_intron",
                "functional_annotations": [
                    "intron_variant",
                    "non_coding_transcript_variant",
                ],
                "region_annotations": ["intronic", "ncRNA_exonic"],
                "intron": "2/5",
                "strand": "+",
                "coding_sequence_name": "n.444-4554G>A",
                "is_canonical": False,
            },
            {
                "transcript_id": "ENST00000469065",
                "hgnc_id": 10729,
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "unknown",
                "biotype": "retained_intron",
                "functional_annotations": ["downstream_gene_variant"],
                "region_annotations": ["downstream"],
                "strand": "+",
                "is_canonical": False,
            },
            {
                "transcript_id": "ENST00000487358",
                "hgnc_id": 10729,
                "sift_prediction": "unknown",
                "polyphen_prediction": "unknown",
                "swiss_prot": "unknown",
                "biotype": "processed_transcript",
                "functional_annotations": [
                    "intron_variant",
                    "non_coding_transcript_variant",
                ],
                "region_annotations": ["intronic", "ncRNA_exonic"],
                "intron": "8/10",
                "strand": "+",
                "coding_sequence_name": "n.1032-4554G>A",
                "is_canonical": False,
            },
        ],
        "functional_annotation": "non_coding_transcript_variant",
        "region_annotation": "ncRNA_exonic",
        "sift_prediction": "unknown",
        "polyphen_prediction": "unknown",
        "hgvs_identifier": "n.1032-4554G>A",
        "canonical_transcript": "ENST00000487358",
        "exon": "",
    }
    return gene


@pytest.fixture
def hgnc_gene():
    """docstring for hgnc_gene"""
    gene = {
        "_id": {"$oid": "5c8112e701f54818d3cbc04a"},
        "hgnc_id": 10729,
        "hgnc_symbol": "SEMA4A",
        "ensembl_id": "ENSG00000196189",
        "chromosome": "1",
        "start": 156117157,
        "end": 156147543,
        "length": 30386,
        "description": "semaphorin 4A",
        "aliases": ["SEMA4A", "SEMAB", "CORD10", "SemB", "FLJ12287"],
        "primary_transcripts": ["NM_022367"],
        "inheritance_models": ["AD", "AR"],
        "phenotypes": [
            {
                "mim_number": 610283,
                "description": "Cone-rod dystrophy 10",
                "inheritance_models": ["AR"],
                "status": "established",
            },
            {
                "mim_number": 610282,
                "description": "Retinitis pigmentosa 35",
                "inheritance_models": ["AD", "AR"],
                "status": "established",
            },
        ],
        "entrez_id": 64218,
        "omim_id": 607292,
        "ucsc_id": "uc001fnl.4",
        "uniprot_ids": ["Q9H3S1"],
        "vega_id": "OTTHUMG00000014042",
        "pli_score": 0.615371620982326,
        "incomplete_penetrance": False,
        "build": "37",
        "transcripts": [
            {
                "_id": {"$oid": "5c81130601f54818d3cc0514"},
                "ensembl_transcript_id": "ENST00000355014",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156119810,
                "end": 156147535,
                "is_primary": False,
                "refseq_id": "NM_001193301",
                "refseq_identifiers": ["NM_001193301"],
                "build": "37",
                "length": 27725,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0516"},
                "ensembl_transcript_id": "ENST00000368285",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156123318,
                "end": 156147535,
                "is_primary": True,
                "refseq_id": "NM_022367",
                "refseq_identifiers": ["NM_001193300", "NM_022367", "XM_005245441"],
                "build": "37",
                "length": 24217,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0517"},
                "ensembl_transcript_id": "ENST00000368284",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156123369,
                "end": 156147534,
                "is_primary": False,
                "refseq_id": "NM_001193302",
                "refseq_identifiers": ["NM_001193302"],
                "build": "37",
                "length": 24165,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0520"},
                "ensembl_transcript_id": "ENST00000368286",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156123388,
                "end": 156147534,
                "is_primary": False,
                "build": "37",
                "length": 24146,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0519"},
                "ensembl_transcript_id": "ENST00000368282",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156124162,
                "end": 156147543,
                "is_primary": False,
                "refseq_id": "XM_005245442",
                "refseq_identifiers": ["XM_005245442", "XM_005245444", "XM_005245443"],
                "build": "37",
                "length": 23381,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc051b"},
                "ensembl_transcript_id": "ENST00000487358",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156126216,
                "end": 156145023,
                "is_primary": False,
                "build": "37",
                "length": 18807,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc051e"},
                "ensembl_transcript_id": "ENST00000462892",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156131018,
                "end": 156145438,
                "is_primary": False,
                "build": "37",
                "length": 14420,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0512"},
                "ensembl_transcript_id": "ENST00000435124",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156117157,
                "end": 156131289,
                "is_primary": False,
                "build": "37",
                "length": 14132,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0513"},
                "ensembl_transcript_id": "ENST00000414683",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156119514,
                "end": 156131284,
                "is_primary": False,
                "build": "37",
                "length": 11770,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0518"},
                "ensembl_transcript_id": "ENST00000438830",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156123398,
                "end": 156130819,
                "is_primary": False,
                "build": "37",
                "length": 7421,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc0515"},
                "ensembl_transcript_id": "ENST00000485575",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156119994,
                "end": 156126365,
                "is_primary": False,
                "build": "37",
                "length": 6371,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc051a"},
                "ensembl_transcript_id": "ENST00000470306",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156124668,
                "end": 156128822,
                "is_primary": False,
                "build": "37",
                "length": 4154,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc051d"},
                "ensembl_transcript_id": "ENST00000469065",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156130741,
                "end": 156133089,
                "is_primary": False,
                "build": "37",
                "length": 2348,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc051f"},
                "ensembl_transcript_id": "ENST00000484155",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156145124,
                "end": 156146447,
                "is_primary": False,
                "build": "37",
                "length": 1323,
            },
            {
                "_id": {"$oid": "5c81130601f54818d3cc051c"},
                "ensembl_transcript_id": "ENST00000466698",
                "hgnc_id": 10729,
                "chrom": "1",
                "start": 156130335,
                "end": 156131460,
                "is_primary": False,
                "build": "37",
                "length": 1125,
            },
        ],
    }
    return gene


@pytest.fixture
def sv_var_obj():
    sv_var = {
        "_id": "19ecad237722da35ec5ed01ecc9f0c3b",
        "length": 1,
        "mate_id": null,
        "document_id": "19ecad237722da35ec5ed01ecc9f0c3b",
        "end_chrom": "1",
        "variant_id": "9657183743c80ef8552ef7725c0f4bef",
        "freebayes": "Pass",
        "reference": "A",
        "category": "snv",
        "spidex": 1.7039999961853027,
        "institute": "cust003",
        "dbsnp_id": "rs147223770",
        "hgnc_ids": [7882],
        "end": 120478125,
        "compounds": [
            {
                "display_name": "1_120602372_A_G",
                "not_loaded": false,
                "variant": "cd6c106e6010a97d20dce3265a7b527a",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 25,
                "rank_score": 9,
            },
            {
                "display_name": "1_120576878_C_A",
                "not_loaded": false,
                "variant": "d334f56b68089c490a130f6707d05a52",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 24,
                "rank_score": 8,
            },
            {
                "display_name": "1_120464481_T_C",
                "not_loaded": false,
                "variant": "e1b3a61989b641b5173a68c94960dac7",
                "genes": [
                    {
                        "functional_annotation": "intron_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "intronic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 22,
                "rank_score": 6,
            },
            {
                "display_name": "1_120500463_A_ACACC",
                "not_loaded": false,
                "variant": "61f871950ff8c599df4d6513f959bb9e",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 22,
                "rank_score": 6,
            },
            {
                "display_name": "1_120560920_T_C",
                "not_loaded": false,
                "variant": "7f6a7dc349249fdcecbf23d084744a1f",
                "genes": [
                    {
                        "functional_annotation": "non_coding_transcript_variant",
                        "hgnc_id": 7882,
                        "region_annotation": "ncRNA_exonic",
                        "hgnc_symbol": "NOTCH2",
                    }
                ],
                "combined_score": 22,
                "rank_score": 6,
            },
        ],
        "samples": [
            {
                "genotype_quality": 99,
                "display_name": "25-1-1A",
                "read_depth": 38,
                "genotype_call": "0/1",
                "allele_depths": [22, 16],
                "sample_id": "SVE2126A23",
            },
            {
                "genotype_quality": 99,
                "display_name": "25-2-1U",
                "read_depth": 26,
                "genotype_call": "0/1",
                "allele_depths": [13, 13],
                "sample_id": "ACC3320A8",
            },
            {
                "genotype_quality": 99,
                "display_name": "25-2-2U",
                "read_depth": 33,
                "genotype_call": "0/0",
                "allele_depths": [33, 0],
                "sample_id": "ACC3320A9",
            },
        ],
        "panels": [
            "NJU",
            "MSKI",
            "PEDHEP",
            "panel1",
            "OMIM-AUTO",
            "SKD",
            "PIDCAD",
            "IEM",
            "ID",
            "OMIM",
        ],
        "variant_rank": 18,
        "local_obs_old": 4,
        "missing_data": false,
        "rank_score": 16,
        "chromosome": "1",
        "display_name": "1_120478125_A_C_clinical",
        "variant_type": "clinical",
        "case_id": "soundclam",
        "clnsig": [{"revstat": "single", "accession": "RCV000121717.2", "value": 2}],
        "samtools": "Filtered",
        "cytoband_start": "p12",
        "cadd_score": 29,
        "hgnc_symbols": ["NOTCH2"],
        "rank_score_results": [
            {"score": 3, "category": "Splicing"},
            {"score": 3, "category": "Variant_call_quality_filter"},
            {"score": 1, "category": "Inheritance_Models"},
            {"score": 1, "category": "Clinical_significance"},
            {"score": 5, "category": "Consequence"},
            {"score": 0, "category": "Gene_intolerance_prediction"},
            {"score": 3, "category": "Conservation"},
            {"score": 2, "category": "allele_frequency"},
            {"score": 3, "category": "Deleteriousness"},
            {"score": 1, "category": "Protein_prediction"},
        ],
        "cytoband_end": "p12",
        "thousand_genomes_frequency": 0.001597439986653626,
        "gatk": "Pass",
        "simple_id": "1_120478125_A_C",
        "genetic_models": ["AR_comp", "AR_comp_dn"],
        "quality": 990.1599731445312,
        "filters": ["PASS"],
        "sub_category": "snv",
        "genes": [
            {
                "functional_annotation": "missense_variant",
                "hgnc_id": 7882,
                "sift_prediction": "deleterious",
                "polyphen_prediction": "unknown",
                "ensembl_id": "ENSG00000134250",
                "inheritance": [],
                "description": "notch 2",
                "region_annotation": "exonic",
                "transcripts": [
                    {
                        "smart_domain": "SM00181",
                        "hgnc_id": 7882,
                        "transcript_id": "ENST00000256646",
                        "coding_sequence_name": "c.3625T>G",
                        "sift_prediction": "deleterious",
                        "region_annotations": ["exonic"],
                        "swiss_prot": "Q04721",
                        "functional_annotations": ["missense_variant"],
                        "is_canonical": true,
                        "protein_sequence_name": "p.Phe1209Val",
                        "biotype": "protein_coding",
                        "strand": "-",
                        "protein_id": "ENSP00000256646",
                        "pfam_domain": "PF00008",
                        "prosite_profile": "PS50026",
                        "polyphen_prediction": "unknown",
                        "exon": "22/34",
                    },
                    {
                        "hgnc_id": 7882,
                        "transcript_id": "ENST00000478864",
                        "polyphen_prediction": "unknown",
                        "sift_prediction": "unknown",
                        "region_annotations": ["ncRNA_exonic"],
                        "swiss_prot": "unknown",
                        "functional_annotations": [
                            "non_coding_transcript_exon_variant"
                        ],
                        "is_canonical": false,
                        "biotype": "processed_transcript",
                        "strand": "-",
                        "coding_sequence_name": "n.285T>G",
                        "exon": "2/2",
                    },
                ],
                "hgnc_symbol": "NOTCH2",
            }
        ],
        "alternative": "C",
        "exac_frequency": 0.003318999893963337,
        "position": 120478125,
        "cosmic_ids": null,
    }
    return sv_var
