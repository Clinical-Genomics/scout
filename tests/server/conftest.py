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

@pytest.fixture
def app(real_database_name, real_variant_database, user_obj):

    app = create_app(config=dict(TESTING=True, DEBUG=True, MONGO_DBNAME=real_database_name,
                                 DEBUG_TB_ENABLED=False, LOGIN_DISABLED=True))

    @app.route('/auto_login')
    def auto_login():
        log.debug('Got request for auto login for {}'.format(user_obj))
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    return app


@pytest.fixture
def institute_info():
    _institute_info = dict(internal_id='cust000', display_name='test_institute')
    return _institute_info


@pytest.fixture
def user_info(institute_info):
    _user_info = dict(email='john@doe.com', name='John Doe', roles=['admin','mme_submitter'],
                      institutes=[institute_info['internal_id']])
    return _user_info


@pytest.fixture
def ldap_app(request):
    """app ficture for testing LDAP connections."""
    config = {
        "TESTING": True,
        "DEBUG" : True,
        "SERVER_NAME" : "fakey.server.name",
        "LDAP_HOST" : "ldap://test_ldap_server",
        'WTF_CSRF_ENABLED' : False,
        "MONGO_DBNAME" : "testdb"
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
        "ensembl_id": 
        "ENSG00000196189", 
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
                "is_canonical": False
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
                "is_canonical": False
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
                "is_canonical": False
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
                "is_canonical": True
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
                "is_canonical": False
            }, 
            {
                "transcript_id": "ENST00000462892", 
                "hgnc_id": 10729, 
                "sift_prediction": "unknown", 
                "polyphen_prediction": "unknown", 
                "swiss_prot": "unknown", 
                "biotype": "retained_intron", 
                "functional_annotations": ["intron_variant", 
                "non_coding_transcript_variant"], 
                "region_annotations": ["intronic", "ncRNA_exonic"], 
                "intron": "2/5", 
                "strand": "+", 
                "coding_sequence_name": "n.444-4554G>A", 
                "is_canonical": False
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
                "is_canonical": False
            }, 
            {
                "transcript_id": "ENST00000487358", 
                "hgnc_id": 10729, 
                "sift_prediction": "unknown", 
                "polyphen_prediction": "unknown", 
                "swiss_prot": "unknown", 
                "biotype": "processed_transcript", 
                "functional_annotations": ["intron_variant", "non_coding_transcript_variant"], 
                "region_annotations": ["intronic", "ncRNA_exonic"], 
                "intron": "8/10", 
                "strand": "+", 
                "coding_sequence_name": "n.1032-4554G>A", 
                "is_canonical": False
            }
        ], 
        "functional_annotation": "non_coding_transcript_variant", 
        "region_annotation": "ncRNA_exonic", 
        "sift_prediction": "unknown", 
        "polyphen_prediction": "unknown", 
        "hgvs_identifier": "n.1032-4554G>A", 
        "canonical_transcript": "ENST00000487358", 
        "exon": ""
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
        "description": 
        "semaphorin 4A", 
        "aliases": ["SEMA4A", "SEMAB", "CORD10", "SemB", "FLJ12287"], 
        "primary_transcripts": ["NM_022367"], 
        "inheritance_models": ["AD", "AR"], 
        "phenotypes": [
            {
                "mim_number": 610283, 
                "description": "Cone-rod dystrophy 10", 
                "inheritance_models": ["AR"], 
                "status": "established"
            }, 
            {
                "mim_number": 610282, 
                "description": "Retinitis pigmentosa 35", 
                "inheritance_models": ["AD", "AR"], 
                "status": "established"
            }
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
                "length": 27725
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
                "length": 24217
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
                "length": 24165
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
                "length": 24146
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
                "length": 23381
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
                "length": 18807
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
                "length": 14420
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
                "length": 14132
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
                "length": 11770
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
                "length": 7421
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
                "length": 6371
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
                "length": 4154
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
                "length": 2348
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
                "length": 1323
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
                "length": 1125
            }
        ]
    }
    return gene