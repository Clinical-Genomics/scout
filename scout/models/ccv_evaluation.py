# -*- coding: utf-8 -*-
"""
scout.models.ccv_evaluation
~~~~~~~~~~~~~~~~~~

Define a document to describe a ClinGen-CGC-VIGG evaluation

Evaluations are stored in its own collection

"""

from datetime import datetime

ccv_evaluation = dict(
    variant_specific=str,  # md5 document id
    variant_id=str,  # md5 variant id
    institute_id=str,  # Institute _id, required
    case_id=str,  # case_id, required
    classification=str,  # What did the evaluation end up in?
    # All evaluations will have an author
    user_id=str,  # user email, required
    user_name=str,  # user name
    criteria=list,  # List of dictionaries with criterias
    # timestamps
    created_at=datetime,
)
