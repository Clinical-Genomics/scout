# -*- coding: utf-8 -*-
import logging

from pymongo import ASCENDING

LOG = logging.getLogger(__name__)

class DiagnoseHandler(object):

    def omim_terms(self, query=None, omim_term=None, text=None, limit=None):
        """Return all OMIM terms

        If a query is sent omim_id will try to match with regex on term or
        description.

        Args:
            query(str): Part of a OMIM term or description
            omim_term(str): Search for a specific OMIM term
            text(str): Text search terms separated by space
            limit(int): the number of desired results

        Returns:
            result(pymongo.Cursor): A cursor with OMIM terms
        """

        query_dict = {}
        search_term = None
        if query:
            query_dict = {
                "$or": [
                    {"disease_nr": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                ]
            }
            search_term = query
        elif text:
            new_string = ""
            for i, word in enumerate(text.split(" ")):
                if i == 0:
                    new_string += word
                else:
                    new_string += ' "{0}"'.format(word)
            LOG.info("Search OMIM terms with %s", new_string)
            query_dict["$text"] = {"$search": new_string}
            search_term = text
        elif hpo_term:
            query_dict["disease_id"] = hpo_term
            search_term = hpo_term

        limit = limit or int(10e10)
        res = (
            self.disease_term_collection.find(query_dict)
            .limit(limit)
            .sort("disease_nr", ASCENDING)
        )
        return res
