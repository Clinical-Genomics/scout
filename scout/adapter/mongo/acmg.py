# -*- coding: utf-8 -*-
import logging

from bson import ObjectId
import pymongo

from scout.utils.acmg import get_acmg
from scout.build.acmg import build_evaluation
from scout.constants import ACMG_MAP

log = logging.getLogger(__name__)


class ACMGHandler(object):
    def submit_evaluation(
        self,
        variant_obj,
        user_obj,
        institute_obj,
        case_obj,
        link,
        criteria=None,
        classification=None,
    ):
        """Submit an evaluation to the database

        Get all the relevant information, build a evaluation_obj

        Args:
            variant_obj(dict)
            user_obj(dict)
            institute_obj(dict)
            case_obj(dict)
            link(str): variant url
            criteria(list(dict)):
                                            [
                                        {
                                        'term': str,
                                        'comment': str,
                                        'links': list(str)
                                        },
                                        .
                                        .
                                    ]
            classification(int)
        """
        criteria = criteria or []

        variant_specific = variant_obj["_id"]
        variant_id = variant_obj["variant_id"]
        user_id = user_obj["_id"]
        user_name = user_obj.get("name", user_obj["_id"])
        institute_id = institute_obj["_id"]
        case_id = case_obj["_id"]

        evaluation_terms = [evluation_info["term"] for evluation_info in criteria]

        if classification is None:
            classification = get_acmg(evaluation_terms)

        if classification:
            evaluation_obj = build_evaluation(
                variant_specific=variant_specific,
                variant_id=variant_id,
                user_id=user_id,
                user_name=user_name,
                institute_id=institute_id,
                case_id=case_id,
                classification=classification,
                criteria=criteria,
            )

            self._load_evaluation(evaluation_obj)

        # Update the acmg classification for the variant:
        self.update_acmg(institute_obj, case_obj, user_obj, link, variant_obj, classification)
        return classification

    def _load_evaluation(self, evaluation_obj):
        """Load a evaluation object into the database"""
        res = self.acmg_collection.insert_one(evaluation_obj)
        return res

    def delete_evaluation(self, evaluation_obj):
        """Delete an evaluation from the database

        Args:
            evaluation_obj(dict)

        """
        self.acmg_collection.delete_one({"_id": evaluation_obj["_id"]})

    def get_evaluation(self, evaluation_id):
        """Get a single evaluation from the database

        Args:
            evaluation_id(str)

        """
        return self.acmg_collection.find_one({"_id": ObjectId(evaluation_id)})

    def get_evaluations(self, variant_obj):
        """Return all evaluations for a certain variant.

        Args:
            variant_obj (dict): variant dict from the database

        Returns:
            pymongo.cursor: database cursor
        """
        query = dict(variant_id=variant_obj["variant_id"])
        res = self.acmg_collection.find(query).sort([("created_at", pymongo.DESCENDING)])
        return res
