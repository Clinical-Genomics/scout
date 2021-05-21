"""Query and updates tags and dismiss nomenclature."""

import logging
from datetime import datetime

import pymongo

LOG = logging.getLogger(__name__)


class VariantEvaluationHandler(object):
    """Interact with variant evaluation information."""

    def add_evaluation_term(self, evaluation_term_obj):
        """Add evaluation term for a institute."""
        self.evaluation_terms_collection.insert_one(evaluation_term_obj)

    def evaluation_terms(self, term_category=None, analysis_type=None, institute_id=None):
        """List evaluation terms used by a institute."""
        query = {}
        if term_category:
            query["term_category"] = term_category

        target_institutes = ["all"]
        if institute_id:
            target_institutes.append(institute_id)

        target_analysis_types = ["all"]
        if analysis_type:
            target_analysis_types.append(analysis_type)

        query = {
            "analysis_type": {"$in": target_analysis_types},
            "institute": {"$in": target_institutes},
            **query,
        }
        LOG.debug(f'query for terms: "{query}"')
        return self.evaluation_terms_collection.find(query, sort=[("rank", pymongo.ASCENDING)])

    def get_evaluation_term(
        self, term_category, term_id=None, rank=None, analysis_type=None, institute_id=None
    ):
        """Get evaluation term data."""
        # for backwards compat
        if not term_id and not rank:
            raise ValueError("neither internal_id nor rank was provided")
        query = {}
        if term_id:
            query["internal_id"] = term_id

        if rank:
            query["rank"] = rank

        target_institutes = ["all"]
        if institute_id:
            target_institutes.append(institute_id)

        target_analysis_types = ["all"]
        if analysis_type:
            target_analysis_types.append(analysis_type)

        # build final query
        query = {
            **query,
            "term_category": term_category,
            "analysis_type": {"$in": target_analysis_types},
            "institute": {"$in": target_institutes},
        }
        return self.evaluation_terms_collection.find_one(query, sort=[("rank", pymongo.ASCENDING)])
