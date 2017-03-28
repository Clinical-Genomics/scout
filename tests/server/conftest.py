# -*- coding: utf-8 -*-
import logging

import pytest
import pymongo

from scout.server.app import create_app
from scout.adapter import PymongoAdapter
from scout.load.hgnc_gene import load_hgnc_genes
from scout.load.hpo import load_hpo
from scout.load.panel import load_panel


log = logging.getLogger(__name__)


@pytest.fixtures
def database_name(request):
    db_name = 'realtestdb'
    return db_name


@pytest.fixture
def app(database_name):
    app = create_app(config=dict(DEBUG_TB_ENABLED=False, MONGO_DBNAME=database_name))
    return app


@pytest.yield_fixture(scope='session')
def real_database(database_name, institute_obj, user_obj, genes, gene_database,
                  hpo_terms_handle, genemap_handle, panel_info, case_obj, variant_objs):
    """Setup a real database with populated data"""
    mongo_client = pymongo.MongoClient()

    database = mongo_client[database_name]
    adapter = PymongoAdapter(database)

    # Populate the database
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)

    load_hgnc_genes(adapter, genes)

    log.info("Creating index on hgnc collection")
    adapter.hgnc_collection.create_index([('build', pymongo.ASCENDING),
                                          ('hgnc_symbol', pymongo.ASCENDING)])

    load_hpo(adapter=gene_database, hpo_lines=hpo_terms_handle, disease_lines=genemap_handle)
    load_panel(adapter=adapter, panel_info=panel_info)
    adapter.add_case(case_obj)

    for variant in variant_objs:
        adapter.load_variant(variant)

    yield adapter

    mongo_client.drop_database(database_name)
