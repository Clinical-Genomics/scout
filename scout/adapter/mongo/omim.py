# -*- coding: utf-8 -*-
import logging

from pymongo import ASCENDING

LOG = logging.getLogger(__name__)

class DiagnosisHandler(object):
    """Class for handling OMIM and disease-related database objects"""
    
    def omim_terms(self, query=None, limit=None):
        """Return all OMIM terms

        If a query is sent omim_id will try to match with regex on term or
        description.

        Args:
            query(str): Part of a OMIM term or description
            limit(int): the number of desired results

        Returns:
            result(pymongo.Cursor): A cursor with OMIM terms
        """

        query_dict = {}
        search_term = None
        if query:
            query_dict = {
                "$or": [
                    {"disease_nr": {"$regex": query, "$options": "i"}}, #case insensitive
                    {"description": {"$regex": query, "$options": "i"}}, #case insensitive
                ]
            }
            search_term = query

        LOG.info('IN ADAPTER, query is {}'.format(query_dict))

        limit = limit or int(10e10)
        res = (
            self.disease_term_collection.find(query_dict)
            .limit(limit)
            .sort("disease_nr", ASCENDING)
        )

        return res

    def disease_term(self, disease_identifier):
        """Return a disease term

        Checks if the identifier is a disease number or a id

        Args:
            disease_identifier(str)

        Returns:
            disease_obj(dict)
        """
        query = {}
        try:
            disease_identifier = int(disease_identifier)
            query["disease_nr"] = disease_identifier
        except ValueError:
            query["_id"] = disease_identifier

        return self.disease_term_collection.find_one(query)

    def disease_terms(self, hgnc_id=None):
        """Return all disease terms that overlaps a gene

            If no gene, return all disease terms

        Args:
            hgnc_id(int)

        Returns:
            iterable(dict): A list with all disease terms that match
        """
        query = {}
        if hgnc_id:
            LOG.debug("Fetching all diseases for gene %s", hgnc_id)
            query["genes"] = hgnc_id
        else:
            LOG.info("Fetching all disease terms")

        return list(self.disease_term_collection.find(query))

    def load_disease_term(self, disease_obj):
        """Load a disease term into the database

        Args:
            disease_obj(dict)
        """
        LOG.debug("Loading disease term %s into database", disease_obj["_id"])
        try:
            self.disease_term_collection.insert_one(disease_obj)
        except DuplicateKeyError as err:
            raise IntegrityError(
                "Disease term %s already exists in database".format(disease_obj["_id"])
            )

        LOG.debug("Disease term saved")
