"""Load an evaluation term into the database."""


import datetime
import logging

import pymongo

LOG = logging.getLogger(__name__)


def load_evaluation_term(
    adapter,
    internal_id,
    name,
    description,
    term_category,
    rank=None,
    institute="all",
    analysis_type="all",
    **kwargs,
):
    """Load a evaluation term into the database.

    Mandatory terms are:
        internal_id: unique id of a term
        name: displayed name of a term
        label: displayed shorthand name of a term
        description: full description of a term
        rank: unique integer for displaying terms in a given order
        institute: limit the term to a an [institution_id|all]
        term_category: the type of term
        analysis_type: limit the term to a given analysis type
        **kwargs: other variables to be associated with the term
    """
    if internal_id:  # verify unique internal_id
        resp = adapter.evaluation_terms_collection.find_one(
            {"internal_id": internal_id, "term_category": term_category}
        )
        if resp is not None:
            raise ValueError(f'internal_id "{internal_id}" is not unique')

    if rank is not None:  # verify unique rank
        resp = adapter.evaluation_terms_collection.find_one(
            {"rank": rank, "term_category": term_category}
        )
        if resp is not None:
            raise ValueError(f'rank "{rank}" is not unique')
    else:  # get latest rank and increment with one
        query = {
            "term_category": term_category,
        }
        rank_query = adapter.evaluation_terms_collection.find_one(
            query, sort=[("rank", pymongo.DESCENDING)]
        )
        last_rank = rank_query["rank"] if rank_query else 0
        # rank to the next rank in the order
        rank = last_rank + 1

    # store new database object
    evaluation_term_obj = dict(
        internal_id=internal_id,
        name=name,
        description=description,
        term_category=term_category,
        rank=rank,
        institute=institute,
        analysis_type=analysis_type,
        last_modified=datetime.datetime.utcnow(),
        **kwargs,
    )
    adapter.add_evaluation_term(evaluation_term_obj)
