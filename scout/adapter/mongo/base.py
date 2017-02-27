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
        self.user_collection = database.user
        self.institute_collection = database.institute
        self.event_collection = database.event
        self.case_collection = database.case
        self.panel_collection = database.panel
        # This will be used during the transfer to pymongo
        self.mongoengine_adapter = MongoEngineAdapter()

    def getoradd_user(self, email, name, location=None, institutes=None):
        """Get or create a new user."""
        
        user_obj = self.user(email=email)
        
        if user_obj is None:
            logger.info('create user: %s', email)
            self.user_collection.insert_one({
                '_id': email,
                'email': email,
                'created_at': datetime.now(),
                'location': location,
                'name': name,
                'institutes': institutes,
            })
            user_obj = self.user(email=email)

        return user_obj

    def add_user(self, user_obj):
        """Add a user object to the database
        
            Args:
                user_obj(dict): A dictionary with user information
        """
        logger.info("Adding user to the database")
        user_obj['_id'] = user_obj['email']
        user_obj['created_at'] = datetime.now()
        self.user_collection.insert_one(user_obj)
        logger.debug("User inserted")

    def user(self, email=None):
        """Fetch a user from the database."""
        logger.info("Fetching user %s", email)
        user_obj = self.user_collection.find_one({'_id': email})
        
        if user_obj:
            institutes = []
            for institute_id in user_obj['institutes']:
                institute_obj = self.institute(institute_id=institute_id)
                if not institute_obj:
                    logger.warning("Institute %s not in database", institute_id)
                    ##TODO Raise exception here?
                else:
                    institutes.append(institute_obj)
            user_obj['institutes'] = institutes
        
        return user_obj

    def update_access(self, user_obj):
        self.mongoengine_adapter.update_access(user_obj=user_obj)
