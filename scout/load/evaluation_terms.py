"""Load an evaluation term into the database."""


import logging

from scout.build import build_evaluation_term
import datetime

LOG = logging.getLogger(__name__)


def load_evaluation_term(adapter, internal_id, label, description, evidence, institute=None):
    """Load a evaluation term into the database."""

    evaluation_term_obj = dict(
        internal_id=internal_id,
        label=label,
        institute=institute,
        description=description,
        evidence=evidence,
        last_modified: datetime.datetime.utcnow(),
    )
    adapter.add_evaluation_term(evaluation_term_obj)
