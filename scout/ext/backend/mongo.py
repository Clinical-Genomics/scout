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
import json
import click
import logging

from mongoengine import connect, DoesNotExist, Q

import phizz


from . import EventHandler, VariantHandler
from scout.models import (Variant, Case, Institute, PhenotypeTerm)
from scout.ext.backend.utils import (build_query)

logger = logging.getLogger(__name__)

class MongoAdapter(EventHandler, VariantHandler):
    """Adapter for cummunication with a mongo database."""
    
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
        
            database(str): Name of database
            host(str): Host of database
            port(int): Port of database
            username(str)
            password(str)
        """
        logger.info("Connecting to database {0}".format(database))
        connect(
            database, 
            host=host, 
            port=port, 
            username=username,
            password=password
        )
        logger.debug("Connection established")
        
    def __init__(self, app=None):
        if app:
            logger.info("Initializing app")
            self.init_app(app)

    def institute(self, institute_id):
        """Fetch an Institute from the database
        
        Args:
            institute_id(str): An Institute id
    
        Returns:
            An Institute object
        """
        logger.info("Fetching institute {0}".format(
            institute_id))
        try:
            result = Institute.objects.get(internal_id=institute_id)
        except DoesNotExist:
            result = None
        return result

    def cases(self, collaborator=None, query=None):
        """Fetches all cases from the backend.

        Args:
            collaborator(str): If collaborator should be considered
            query(dict): If a specific query is used
        
        Yields:
            Cases ordered by date
        """
        logger.info("Fetch all cases")
        if collaborator:
            logger.info("Use collaborator {0}".format(collaborator))
            case_query = Case.objects(collaborators=collaborator)
        else:
            case_query = Case.objects

            if query:
                # filter cases by matching display name of case or individuals
                case_query = case_query.filter(Q(display_name__contains=query) |
                Q(individuals__display_name__contains=query))

        return case_query.order_by('-updated_at')

    def case(self, institute_id, case_id):
        """Fetches a single case from database

        Args:
            institute_id(str)
            case_id(str)

        Yields:
            A single Case
        """
        
        logger.info("Fetch case {0} from institute {1}".format(
            case_id, institute_id))
        try:
            return Case.objects.get(
                collaborators__contains=institute_id,
                display_name=case_id
            )
        except DoesNotExist:
            logger.warning("Could not find case {0}".format(case_id))
            return None

    def gene_panel(self, panel_id, version):
        """Fetch a gene panel from the database."""
        return dict()

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

