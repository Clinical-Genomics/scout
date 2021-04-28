"""Query and updates tags and dismiss nomenclature."""

import logging
from datetime import datetime
import pymongo

LOG = logging.getLogger(__name__)


class VariantEvaluationHandler(object):
    """Interact with variant evalutation information."""

    def add_evaluation_term(self, evaluation_term_obj):
        """Add evalutation term for a institute."""
        self.evaluation_terms_collection.insert_one(evaluation_term_obj)

    def update_evaluation_term(self, institute_obj, term_id, evaluation_term_obj):
        """Update an existing term."""
        self.evaluation_terms_collection.update()

    def drop_evaluation_terms(self):
        """Drop term collection from database"""
        self.evaluation_terms_collection.drop()
        LOG.info("Dropped the evaluation terms collection from database")

    def evaluation_terms(self, term_category, institute_id=None):
        """List evaluation terms used by a institute."""
        target_institutes = ["all"]
        if institute_id:
            target_institutes.append(institute_id)
        query = {"type": term_category, "institute": {"$in": target_institutes}}
        return self.evaluation_terms_collection.find(query, sort=[("rank", pymongo.ASCENDING)])
