"""Query and updates tags and dismiss nomenclature."""

import logging
from datetime import datetime

import pymongo

from scout.constants.case_tags import TRACKS
from scout.constants.variant_tags import EVALUATION_TERM_CATEGORIES

LOG = logging.getLogger(__name__)


class EvaluationTerm(object):
    """Represents a variant evaluation term"""

    def __init__(self, term_obj):
        self.key = term_obj.get("term_key")  # mandatory
        self.label = term_obj.get("term_label")  # mandatory
        self.description = term_obj.get("term_description")  # mandatory
        self.category = term_obj.get("term_category")  # mandatory
        self.tracks = term_obj.get("term_tracks")  # mandatory
        if term_obj.get("term_name"):
            self.name = term_obj["term_name"]
        if term_obj.get("term_evidence"):
            self.evidence = term_obj["term_evidence"]
        if term_obj.get("label_class"):
            self.label_class = term_obj["label_class"]

        self._validate_self()

    def _validate_self(self):
        """Make sure the term category is among the vategories listed in EVALUATION_TERM_CATEGORIES (scout.contants.variant_tags)
        Args:
            category(str):
        """
        if self.key is None:
            raise ValueError(f"Variant evaluation terms key is missing!")
        if self.label is None:
            raise ValueError(f"Variant evaluation terms label can't be null")
        if self.description is None:
            raise ValueError(f"Variant evaluation terms description can't be null")
        if self.category not in EVALUATION_TERM_CATEGORIES:
            raise ValueError(
                f"Variant evaluation term category 'category' is not valid. Valid categories: {EVALUATION_TERM_CATEGORIES}"
            )
        if len(self.tracks) == 0:
            raise ValueError(
                f"At least a track type should be provided for this term. Valid tracks:{TRACKS}"
            )
        for track in self.tracks:
            if track not in TRACKS:
                raise ValueError(
                    f"Variant evaluation terms track '{track}' is not valid. Valid tracks:{TRACKS}"
                )

    def __repr__(self):
        """Return a dictionary representation of this object"""
        return self.__dict__


class VariantEvaluationHandler(object):
    """Interact with variant evaluation information."""

    def load_evaluation_term(self, category, tracks, term_key, term_value):
        """Load a default evaluation term into the database

        Args:
            category(str):

        """
        term_dict = {
            "term_key": term_key,
            "term_category": category,
            "term_tracks": tracks,
            "term_label": term_value.get("label"),
            "term_description": term_value.get("description"),
            "term_name": term_value.get("name"),
            "term_evidence": term_value.get("evidence"),
            "label_class": term_value.get("label_class"),
        }
        evaluation_term = EvaluationTerm(term_dict)
        self.evaluation_terms_collection.insert_one(evaluation_term.__repr__())

    def manual_rank_options(self, tracks):
        """Return all manual rank evaluation terms for the given tracks.

        Args:
            tracks(list): ["rare", "cancer"]

        Returns:
            manual_rank_options(dict): Dictionary containing manual rank options ready to be used in server templates
        """

        manual_rank_terms = self._get_evaluation_terms("manual_rank", tracks)
        return manual_rank_terms

    def dismiss_variant_options(self, tracks):
        """Return all variant dismiss options for the given tracks.

        Args:
            tracks(list): ["rare", "cancer"]

        Returns:
            dismiss_variant_terms(dict): Dictionary containing dismiss variant options ready to be used in server templates
        """
        dismiss_variant_terms = self._get_evaluation_terms("dismissal_term", tracks)
        return dismiss_variant_terms

    def cancer_tier_terms(self):
        """Returns all cancer tier terms in database, formatted as needed by templates"""
        cancer_tier_terms = self._get_evaluation_terms("cancer_tier", ["cancer"])
        return cancer_tier_terms

    def mosaicism_options(self):
        """Return mosaicism options terms in database, formattes as neeeded by templates"""
        mosaicism_terms = self._get_evaluation_terms("mosaicism_options", ["rare"])
        return mosaicism_terms

    def _get_evaluation_terms(self, category, tracks):
        """Return evaluation terms for the given category and tracks.

        Args:
            category(str): "manual_rank" or "dismissal_term"
            tracks(list): ["rare", "cancer"]

        Returns:
            evaluation_terms(dict): Dictionary containing evaluation terms ready to be used in server templates
        """

        evaluation_terms = {}
        query = {"category": category, "tracks": {"$in": tracks}}
        results = self.evaluation_terms_collection.find(query)

        # format terms as expected by templates
        for term in results:
            key = term["key"]
            evaluation_terms[key] = dict(
                label=term["label"],
                description=term["description"],
            )
            if term.get("name"):
                evaluation_terms[key]["name"] = term["name"]

            if term.get("term_evidence"):
                evaluation_terms[key]["term_evidence"] = term["term_evidence"]

            if term.get("label_class"):
                evaluation_terms[key]["label_class"] = term["label_class"]

        return evaluation_terms

    def drop_evaluation_terms(self, category=[]):
        """Delete from database variant evaluation terms from one or more categories

        Args:
            category(list): Any term specified in EVALUATION_TERM_CATEGORIES

        Returns:
            deleted_total(int): Total number of deleted terms
        """
        deleted_total = 0
        for ctg in category:
            result = self.evaluation_terms_collection.delete_many({"category": ctg})
            deleted_total += result.deleted_count
        LOG.warning(f"{deleted_total} variant evaluation terms deleted from database.")
