"""Load an evaluation term into the database."""


import logging

import datetime

LOG = logging.getLogger(__name__)


def load_evaluation_term(adapter, internal_id, label, description, term_categroy, institute=None, **kwargs):
    """Load a evaluation term into the database."""

    evaluation_term_obj = dict(
        internal_id=internal_id,
        label=label,
        institute=institute,
        description=description,
        type=term_categroy,
        last_modified=datetime.datetime.utcnow(),
        **kwargs
    )
    adapter.add_evaluation_term(evaluation_term_obj)
