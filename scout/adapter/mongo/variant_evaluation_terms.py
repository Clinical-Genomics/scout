"""Query and updates tags and dismiss nomenclature."""

import logging
from datetime import datetime

LOG = logging.getLogger(__name__)

class VariantEvaluationHandler(object):
    """Interact with variant evalutation information."""

    def add_evaluation_term(self, evaluation_term_obj):
        """Add evalutation term for a institute."""
        self.evaluation_terms_collection.insert_one()

    def update_evaluation_term(self, institute_obj, term_id):
        """Update an existing term."""
        pass

    def evaluation_terms(self, institute_obj):
        """List evaluation terms used by a institute."""
        pass
