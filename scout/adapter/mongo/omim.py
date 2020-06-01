# -*- coding: utf-8 -*-
import logging

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class DiagnosisHandler(object):
    """Class for handling OMIM and disease-related database objects"""

    def query_omim(self, query=None, limit=None):
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
                    {"disease_nr": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                ]
            }

        limit = limit or int(10e10)
        res = (
            self.disease_term_collection.find(query_dict).limit(limit).sort("disease_nr", ASCENDING)
        )
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
        omim_ids = case_obj.get("diagnosis_phenotypes", []) + case_obj.get("diagnosis_genes", [])
        res = self.disease_term_collection.find({"disease_nr": {"$in": omim_ids}}).sort(
            "disease_nr", ASCENDING
        )
        return res

    def omim_to_genes(self, omim_obj):
        """Gets all genes associated to an OMIM term

        Args:
            omim_obj(dict): an OMIM object

        Returns:
            gene_objs(list): a list of gene objects

        """
        gene_objs = []
        if omim_obj:
            gene_objs = [self.hgnc_gene(hgnc_id) for hgnc_id in omim_obj.get("genes", [])]
        return gene_objs

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
