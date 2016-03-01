#!/usr/bin/env python
# encoding: utf-8
"""
mongo.py

This is the mongo adapter for scout, it is a communicator for quering and
updating the mongodatabase.
Implements BaseAdapter.

Created by Måns Magnusson on 2014-11-17.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""
from __future__ import (absolute_import, print_function)
from datetime import datetime
import logging

from mongoengine import connect, DoesNotExist

from . import EventHandler, VariantHandler, CaseHandler
from scout.models import User

logger = logging.getLogger(__name__)


class MongoAdapter(EventHandler, VariantHandler, CaseHandler):

    """Adapter for cummunication with a mongo database."""

    def __init__(self, app=None):
        if app:
            logger.info("Initializing app")
            self.init_app(app)

    def init_app(self, app):
        config = getattr(app, 'config', {})

        host = config.get('MONGODB_HOST', 'localhost')
        port = config.get('MONGODB_PORT', 27017)
        database = config.get('MONGODB_DB', 'variantDatabase')
        username = config.get('MONGODB_USERNAME', None)
        password = config.get('MONGODB_PASSWORD', None)
        self.connect_to_database(
            database,
            host=host,
            port=port,
            username=username,
            password=password
        )

    def connect_to_database(self, database, host='localhost', port=27017,
                            username=None, password=None):
        """Connect to a mongo database

        Args:
            database(str): Name of database
            host(str): Host of database
            port(int): Port of database
            username(str)
            password(str)
        """
        logger.info("Connecting to database {0}".format(database))
        self.mongodb_name = database
        self.db = connect(
            database,
            host=host,
            port=port,
            username=username,
            password=password
        )
        logger.debug("Connection established")

    def drop_database(self):
        """Drop the database that the adapter is connected to."""
        logger.info("Drop database {0}".format(self.mongodb_name))
        self.db.drop_database(self.mongodb_name)
        logger.debug("Database dropped")
        return

    def update_dynamic_gene_list(self, case, gene_list):
        """Update the dynamic gene list for a case

        Arguments:
            case (Case): The case that should be updated
            gene_list (list): The list of genes that should be added
        """
        logger.info("Updating the dynamic gene list for case {0}".format(
            case.display_name))
        case.dynamic_gene_list = gene_list
        case.save()
        logger.debug("Case updated")

    def getoradd_user(self, email, name, location=None, institutes=None):
        """Get or create a new user."""
        try:
            user_obj = User.objects.get(email=email)
        except DoesNotExist:
            logger.info('create user: %s', email)
            user_obj = User(email=email, created_at=datetime.utcnow(),
                            location=location, name=name,
                            institutes=institutes)
            user_obj.save()

        return user_obj

    def user(self, email):
        """Fetch a user from the database."""
        user_obj = User.objects.get(email=email)
        return user_obj

    def update_access(self, user_obj):
        user_obj.accessed_at = datetime.utcnow()
        user_obj.save()
