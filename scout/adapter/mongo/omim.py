# -*- coding: utf-8 -*-
import logging
from typing import Iterable, List, Optional, Union

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)

DISEASE_FILTER_PROJECT = {"hpo_terms": 0, "genes": 0}


class DiagnosisHandler(object):
    """Class for handling OMIM and disease-related database objects"""

    def query_omim(self, query: str = None, limit: int = None) -> Iterable:
        """Return all OMIM terms

        If a query is sent omim_id will try to match with regex on term or
        description.
        """

        query_dict = {}
        if query:
            query_dict = {
                "$and": [
                    {
                        "$or": [
                            {"disease_nr": {"$regex": query, "$options": "i"}},
                            {"description": {"$regex": query, "$options": "i"}},
                        ]
                    },
                    {"source": "OMIM"},
                ]
            }

        limit = limit or int(10e10)
        res = (
            self.disease_term_collection.find(query_dict, DISEASE_FILTER_PROJECT)
            .limit(limit)
            .sort("disease_nr", ASCENDING)
        )
        return res

    def convert_diagnoses_format(self, case_obj: dict) -> dict:
        """Convert case OMIM diagnoses from a list of integers (OMIM number) to a list of OMIM terms dictionaries."""
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
        case_diagnoses: List[dict],
        filter_project: Optional[dict] = DISEASE_FILTER_PROJECT,
    ) -> Iterable:
        """Return all complete OMIM diagnoses for a case."""

        omim_ids = [dia["disease_id"] for dia in case_diagnoses]
        query: dict = {"_id": {"$in": omim_ids}}

        return self.disease_term_collection.find(query, filter_project).sort(
            "disease_nr", ASCENDING
        )

    def omim_to_genes(self, omim_obj: dict) -> List[dict]:
        """Gets all genes associated to an OMIM term."""
        gene_objs = []
        if omim_obj:
            gene_objs = [self.hgnc_gene_caption(hgnc_id) for hgnc_id in omim_obj.get("genes", [])]
        return gene_objs

    def disease_term(
        self,
        disease_identifier: Union[str, int],
        filter_project: Optional[dict] = DISEASE_FILTER_PROJECT,
    ) -> dict:
        """Return a disease term after filtering out associated genes and HPO terms (using filter project)."""
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
        filter_project: Optional[dict] = DISEASE_FILTER_PROJECT,
    ) -> list:
        """Return all disease terms for a gene HGNC ID. Optionally filter the returned key/values using filter_project. By default do not return disease-associated genes and HPO terms."""
        query = {}
        if hgnc_id:
            LOG.debug("Fetching all diseases for gene %s", hgnc_id)
            query["genes"] = hgnc_id
        else:
            LOG.info("Fetching all disease terms")

        return list(self.disease_term_collection.find(query, filter_project))

    def load_disease_term(self, disease_obj: dict):
        """Load a disease term into the database-"""
        try:
            self.disease_term_collection.insert_one(disease_obj)
        except DuplicateKeyError:
            raise IntegrityError(
                "Disease term %s already exists in database".format(disease_obj["_id"])
            )
