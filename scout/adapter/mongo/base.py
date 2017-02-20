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

from pymongo import MongoClient

from scout.adapter.mongoengine import MongoEngineAdapter

from .hgnc import GeneHandler
from .case import CaseHandler
from .institute import InstituteHandler
from .event import EventHandler
from .hpo import HpoHandler
from .panel import PanelHandler
from .query import QueryHandler
from .variant import VariantHandler

logger = logging.getLogger(__name__)

class MongoAdapter(GeneHandler, CaseHandler, InstituteHandler, EventHandler,
                    HpoHandler, PanelHandler, QueryHandler, VariantHandler):

    """Adapter for cummunication with a mongo database."""

    def __init__(self, database=None):
        if database:
            self.setup(database)

    def init_app(self, app):
        """Setup via Flask."""
        self.setup(app.extensions['pymongo']['MONGO'][1])

    def setup(self, database):
        """Setup connection to database."""
        self.db = database
        self.hgnc_collection = database.hgnc_gene
        # This will be used during the transfer to pymongo
        self.mongoengine_adapter = MongoEngineAdapter(database)
        print(self.db)

    def getoradd_user(self, email, name, location=None, institutes=None):
        """Get or create a new user."""
        return self.mongoengine_adapter.getoradd_user(
            email=email,
            name=name,
            location=location,
            institutes=institutes
        )

    def user(self, email=None):
        """Fetch a user from the database."""
        return self.mongoengine_adapter.user(email=email)

    def update_access(self, user_obj):
        self.mongoengine_adapter.update_access(user_obj=user_obj)
