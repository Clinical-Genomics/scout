# -*- coding: utf-8 -*-
import logging

from pymongo import ASCENDING

LOG = logging.getLogger(__name__)


class DiagnosisHandler(object):
    def omim_terms(self, query=None, text=None, limit=None):
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

        limit = limit or int(10e10)
        res = (
            self.disease_term_collection.find(query_dict)
            .limit(limit)
            .sort("disease_nr", ASCENDING)
        )
        return res

    def omim_term(self, term):
        """Return one OMIM term

        Args:
            term(str): Search for a specific OMIM term

        Returns:
            res(obj)

        """
        res = self.disease_term_collection.find_one({"_id": term})
        return res

    def case_omim_diagnoses(self, case_obj):
        """Return all complete OMIM diagnoses for a case

        Args:
            case_obj(dict)

        Returns:
            result(pymongo.Cursor): A cursor with OMIM terms

        """
        result = None

        # Collect OMIM terms from case 'diagnosis_phenotypes' and 'diagnosis_genes'
        omim_ids = case_obj.get("diagnosis_phenotypes", []) + case_obj.get(
            "diagnosis_genes", []
        )
        res = self.disease_term_collection.find({"disease_nr": {"$in": omim_ids}}).sort(
            "disease_nr", ASCENDING
        )
        return res

    def omim_genes(self, gene_list):
        """Gets all genes associated to an OMIM term

        Args:
            gene_list(list): a list of hgnc ids

        Returns:
            gene_objs(list): a list of gene objects

        """
        gene_objs = [self.hgnc_gene(hgnc_id) for hgnc_id in gene_list]
        return gene_objs
