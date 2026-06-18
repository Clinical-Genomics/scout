from typing import List, TypedDict

"""
scout.models.acmg_evaluation
~~~~~~~~~~~~~~~~~~

Define a document to describe a ACMG evaluation

Evaluations are stored in its own collection

"""

from datetime import datetime


class Criterion(TypedDict):
    term: str
    comment: str
    links: List[str]
    modifier: str


class Evaluation(TypedDict):
    variant_specific: str  # md5 document id
    variant_id: str  # md5 variant id
    institute_id: str  # Institute _id, required
    case_id: str  # case_id, required
    classification: str  # What did the evaluation end up in?
    # All evaluations will have an author
    user_id: str  # user email, required
    user_name: str  # user name
    criteria: List[Criterion]  # List of dictionaries with criteria
    # timestamps
    created_at: datetime
