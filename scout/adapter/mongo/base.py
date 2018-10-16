#!/usr/bin/env python
# encoding: utf-8
"""
pymongo.py

This is the new mongo adapter for scout that skips mongoengine and uses pymongo,
it is a communicator for quering and updating the mongodatabase.


This is best practice:

 uri = "mongodb://%s:%s@%s" % (
        quote_plus(user), quote_plus(password), host)
    client = MongoClient(uri)

This is to check if server is available:

from pymongo.errors import ConnectionFailure
    client = MongoClient()
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
    except ConnectionFailure:
        print("Server not available")

Created by Måns Magnusson on 2017-02-15.
Copyright (c) 2017 __MoonsoInc__. All rights reserved.

"""
import logging
from datetime import datetime

from .hgnc import GeneHandler
from .case import CaseHandler
from .institute import InstituteHandler
from .event import EventHandler
from .hpo import HpoHandler
from .panel import PanelHandler
from .query import QueryHandler
from .variant import VariantHandler
from .user import UserHandler
from .acmg import ACMGHandler
from .index import IndexHandler
from .clinvar import ClinVarHandler

log = logging.getLogger(__name__)

class MongoAdapter(GeneHandler, CaseHandler, InstituteHandler, EventHandler,
                   HpoHandler, PanelHandler, QueryHandler, VariantHandler,
                   UserHandler, ACMGHandler, IndexHandler, ClinVarHandler):

    """Adapter for cummunication with a mongo database."""

    def __init__(self, database=None):
        if database:
            self.setup(database)

    def init_app(self, app):
        """Setup via Flask."""
        host = app.config.get('MONGO_HOST', 'localhost')
        port = app.config.get('MONGO_PORT', 27017)
        dbname = app.config['MONGO_DBNAME']
        log.info("connecting to database: %s:%s/%s", host, port, dbname)
        self.setup(app.config['MONGO_DATABASE'])

    def setup(self, database):
        """Setup connection to database."""
        self.db = database
        self.hgnc_collection = database.hgnc_gene
        self.user_collection = database.user
        self.whitelist_collection = database.whitelist
        self.institute_collection = database.institute
        self.event_collection = database.event
        self.case_collection = database.case
        self.panel_collection = database.gene_panel
        self.hpo_term_collection = database.hpo_term
        self.disease_term_collection = database.disease_term
        self.variant_collection = database.variant
        self.acmg_collection = database.acmg
        self.clinvar_collection = database.clinvar
        self.clinvar_submission_collection = database.clinvar_submission
        self.exon_collection = database.exon
        self.transcript_collection = database.transcript

    def collections(self):
        """Return all collection names

        Returns:
            collection_names(list(str))
        """
        return self.db.collection_names(include_system_collections=False)

    def __str__(self):
        return "MongoAdapter(db={0})".format(self.db)
