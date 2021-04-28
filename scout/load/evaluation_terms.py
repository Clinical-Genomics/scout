"""Load an evaluation term into the database."""


import logging

import datetime
import pymongo

LOG = logging.getLogger(__name__)


def load_evaluation_term(
    adapter, internal_id, label, description, term_categroy, institute=None, rank=None, **kwargs
):
    """Load a evaluation term into the database."""

    if rank is None:
        query = {
            "institute": institute if institute else "all",
            "sort": [("rank", pymongo.DESCENDING)],
        }
        last_rank = adapter.evaluation_terms_collection.find_one(query)["rank"]
        rank += last_rank

    evaluation_term_obj = dict(
        internal_id=internal_id,
        label=label,
        institute=institute,
        description=description,
        type=term_categroy,
        rank=rank,
        last_modified=datetime.datetime.utcnow(),
        **kwargs
    )
    adapter.add_evaluation_term(evaluation_term_obj)
