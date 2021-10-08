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

from flask import current_app

from .acmg import ACMGHandler
from .case import CaseHandler
from .case_group import CaseGroupHandler
from .clinvar import ClinVarHandler
from .cytoband import CytobandHandler
from .event import EventHandler
from .filter import FilterHandler
from .hgnc import GeneHandler
from .hpo import HpoHandler
from .index import IndexHandler
from .institute import InstituteHandler
from .managed_variant import ManagedVariantHandler
from .matchmaker import MMEHandler
from .omim import DiagnosisHandler
from .panel import PanelHandler
from .phenomodel import PhenoModelHandler
from .query import QueryHandler
from .transcript import TranscriptHandler
from .user import UserHandler
from .variant import VariantHandler

LOG = logging.getLogger(__name__)


class MongoAdapter(
    GeneHandler,
    CaseHandler,
    CaseGroupHandler,
    InstituteHandler,
    EventHandler,
    HpoHandler,
    DiagnosisHandler,
    PanelHandler,
    QueryHandler,
    VariantHandler,
    UserHandler,
    ACMGHandler,
    IndexHandler,
    ClinVarHandler,
    MMEHandler,
    TranscriptHandler,
    FilterHandler,
    ManagedVariantHandler,
    CytobandHandler,
    PhenoModelHandler,
):

    """Adapter for cummunication with a mongo database."""

    def __init__(self, database=None):
        if database:
            self.setup(database)

    def init_app(self, app):
        """Setup via Flask."""
        dbname = app.config["MONGO_DBNAME"]
        LOG.debug(f"Database name: {dbname}")
        self.setup(app.config["MONGO_DATABASE"])

    def setup(self, database):
        """Setup connection to database."""
        self.db = database
        self.hgnc_collection = database.hgnc_gene
        self.user_collection = database.user
        self.institute_collection = database.institute
        self.event_collection = database.event
        self.case_collection = database.case
        self.case_group_collection = database.case_group
        self.panel_collection = database.gene_panel
        self.hpo_term_collection = database.hpo_term
        self.disease_term_collection = database.disease_term
        self.variant_collection = database.variant
        self.acmg_collection = database.acmg
        self.clinvar_collection = database.clinvar
        self.clinvar_submission_collection = database.clinvar_submission
        self.exon_collection = database.exon
        self.transcript_collection = database.transcript
        self.filter_collection = database.filter
        self.cytoband_collection = database.cytoband
        self.managed_variant_collection = database.managed_variant
        self.phenomodel_collection = database.phenomodel

    def collections(self):
        """Return all collection names

        Returns:
            list_collection_names(list(str))
        """
        return self.db.list_collection_names()

    def collection_stats(self, coll_name: str) -> dict:
        """Returns stats from a single collection

        Args:
            coll_name: name of collection to retrieve stats for

        Returns:
            stats(dict): dictionary with collection stats
        """
        db = current_app.config.get("MONGO_DATABASE")
        return db.command("collstats", coll_name)

    def __str__(self):
        return "MongoAdapter(db={0})".format(self.db)
