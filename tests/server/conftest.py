# -*- coding: utf-8 -*-
import logging

import pytest
import pymongo

from scout.server.app import create_app
from scout.adapter import MongoAdapter
from scout.load.hgnc_gene import load_hgnc_genes
from scout.load.hpo import load_hpo

log = logging.getLogger(__name__)

@pytest.fixture
def database_name(request):
    db_name = 'realtestdb'
    return db_name


@pytest.fixture
def app(database_name, real_database):
    app = create_app(config=dict(TESTING=True, DEBUG=True, MONGO_DBNAME=database_name,
                                 DEBUG_TB_ENABLED=False, LOGIN_DISABLED=True))
    return app


@pytest.fixture
def institute_info():
    _institute_info = dict(internal_id='cust000', display_name='test_institute')
    return _institute_info


@pytest.fixture
def user_info(institute_info):
    _user_info = dict(email='john@doe.com', name='John Doe', roles=['admin'],
                      institutes=[institute_info['internal_id']])
    return _user_info


@pytest.fixture
def real_database(request, database_name, institute_obj, user_obj, genes, parsed_panel):
    """Setup a real database with populated data"""
    mongo_client = pymongo.MongoClient()
    mongo_client.drop_database(database_name)

    database = mongo_client[database_name]
    adapter = MongoAdapter(database)

    # Populate the database
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    load_hgnc_genes(adapter, genes)
    adapter.hgnc_collection.create_index([('build', pymongo.ASCENDING),
                                          ('hgnc_symbol', pymongo.ASCENDING)])
    adapter.load_panel(parsed_panel=parsed_panel)

    # load_hpo(adapter=gene_database, hpo_lines=hpo_terms_handle, disease_lines=genemap_handle)
    # adapter.add_case(case_obj)

    # for variant in variant_objs:
    #     adapter.load_variant(variant)

    def teardown():
        mongo_client.drop_database(database_name)

    request.addfinalizer(teardown)

    return adapter
