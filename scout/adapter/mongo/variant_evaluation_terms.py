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
        self.key = term_obj.get("term_key")
        self.label = term_obj["term_label"]
        self.description = term_obj.get("term_description")
        self.category = term_obj.get("term_category")
        self.tracks = term_obj.get("term_tracks")
        if term_obj["term_name"]:
            self.name = term_obj["term_name"]
        if term_obj["term_evidence"]:
            self.evidence = term_obj["term_evidence"]
        if term_obj["label_class"]:
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

    def load_default_evaluation_term(self, category, tracks, term_key, term_value):
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
