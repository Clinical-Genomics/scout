from datetime import datetime

from bson.objectid import ObjectId

""" Represents the document that gets saved/updated in clinvar_submission collection
 for each instute that has cases with ClinVar submission objects """
clinvar_submission = dict(
    _id=ObjectId,
    status=str,  # open, closed
    created_at=datetime,
    institute_id=str,
    variant_data=list,
    case_data=list,
    updated_at=datetime,
    clinvar_subm_id=str,
)

"""Represents the document that gets saved/updated when one or more variants are added
to a ClinVar submission object"""
clinvar = dict(
    _id=str,  # _id of a variant
    Local_ID=str, #(it's actually written ##Local_ID)
    age=int,
    allele_origin=str,
    alt=str,
    Alternate_allele,
)
