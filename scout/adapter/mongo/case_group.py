# -*- coding: utf-8 -*-
import logging

import pymongo

LOG = logging.getLogger(__name__)


class CaseGroupHandler(object):
    """Part of the pymongo adapter that handles case groups.
    Case groups are sets of cases with a common group id, for which user assessments are shared.
    """

    def init_case_group(self, owner):
        """Initialize a case group, creating entry and marking paired case as belonging to group.

        Args:
          owner(str): institute id
        """

        result = self.case_group_collection.insert_one({"owner": owner, "label": "Group"})

        return result.inserted_id

    def remove_case_group(self, case_group_id):
        """Remove a case group.

        Args:
            case_group_id
        """
        result = self.case_group_collection.find_one_and_delete({"_id": case_group_id})

        return result

    def case_group_label(self, case_group_id):
        """Return case group label for case_group.

        Args:
            case_group_id(ObjectId)
        """
        result = self.case_group_collection.find_one({"_id": case_group_id}, {"label": 1})
        label = result.get("label", "unlabeled")

        return label

    def case_group_update_label(self, case_group_id, case_group_label):
        """Change case group label.

        Args:
            case_group_id(ObjectId)
            case_group_label(str)
        """
        result = self.case_group_collection.find_one_and_update(
            {"_id": case_group_id},
            {"$set": {"label": case_group_label}},
        )
        return result
