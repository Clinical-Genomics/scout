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

from . import GeneHandler

logger = logging.getLogger(__name__)


class MongoAdapter(GeneHandler):

    """Adapter for cummunication with a mongo database."""

    def __init__(self, database):
        self.db = database
        self.hgnc_collection = database.hgnc_gene
