# -*- coding: utf-8 -*-
import logging
from typing import Iterator, Optional

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)

DISEASE_FILTER_PROJECT = {"hpo_terms": 0, "genes": 0}


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

    def convert_diagnoses_format(self, case_obj):
        """Convert case OMIM diagnoses from a list of integers (OMIM number) to a list of OMIM terms dictionaries
        Args:
            case_obj(dict)

        Returns:
            updated_case(dict)
        """
        updated_diagnoses = []
        for disease_nr in case_obj.get("diagnosis_phenotypes", []):
            disease_term = self.disease_term(disease_identifier=disease_nr)
            if disease_term is None:
                continue
            updated_diagnoses.append(
                {
                    "disease_nr": disease_nr,
                    "disease_id": disease_term.get("disease_id"),
                    "description": disease_term.get("description"),
                }
            )
        return self.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"diagnosis_phenotypes": updated_diagnoses}},
            return_document=ReturnDocument.AFTER,
        )

    def case_omim_diagnoses(
        self,
        case_diagnoses,
        filter_project: Optional[dict] = DISEASES_FILTER_PROJECT,
    ):
        """Return all complete OMIM diagnoses for a case

        Args:
            case_diagnoses(list) list of case diagnoses dictionaries

        Returns:
            result(pymongo.Cursor): A cursor with OMIM terms

        """
        omim_ids = [dia["disease_id"] for dia in case_diagnoses]
        res = self.disease_term_collection.find({"_id": {"$in": omim_ids}}, filter_project).sort(
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
            gene_objs = [self.hgnc_gene_caption(hgnc_id) for hgnc_id in omim_obj.get("genes", [])]
        return gene_objs

    def disease_term(
        self,
        disease_identifier: Union[str, int],
        filter_project: Optional[dict] = DISEASES_FILTER_PROJECT,
    ) -> dict:
        """Return a disease term."""
        query = {}
        try:
            disease_identifier = int(disease_identifier)
            query["disease_nr"] = disease_identifier
        except ValueError:
            query["_id"] = disease_identifier

        return self.disease_term_collection.find_one(query, filter_project)

    def disease_terms(
        self,
        hgnc_id: Optional[int] = None,
        filter_project: Optional[dict] = DISEASES_FILTER_PROJECT,
    ) -> Iterator:
        """Return all disease terms for a gene HGNC ID."""
        query = {}
        if hgnc_id:
            LOG.debug("Fetching all diseases for gene %s", hgnc_id)
            query["genes"] = hgnc_id
        else:
            LOG.info("Fetching all disease terms")

        return list(self.disease_term_collection.find(query, filter_project))

    def load_disease_term(self, disease_obj):
        """Load a disease term into the database

        Args:
            disease_obj(dict)
        """
        try:
            self.disease_term_collection.insert_one(disease_obj)
        except DuplicateKeyError:
            raise IntegrityError(
                "Disease term %s already exists in database".format(disease_obj["_id"])
            )
