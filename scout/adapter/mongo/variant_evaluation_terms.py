"""Query and updates tags and dismiss nomenclature."""

import logging
from datetime import datetime

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
        LOG.info('Dropped the evaluation terms collection from database')

    def evaluation_terms(self, institute_obj=None):
        """List evaluation terms used by a institute."""
        query = {}
        if institute_obj:
            query['institute'] = institute_obj['internal_id']
        return self.evaluation_terms_collection.find(query)
