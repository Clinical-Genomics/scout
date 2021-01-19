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

        result = self.case_group_collection.insert_one({"owner": owner})

        return result.inserted_id

    def remove_case_group(self, case_group_id):
        """Remove a case group.

        Args:
            case_group_id
        """
        result = self.case_group_collection.find_one_and_delete({"_id": case_group_id})

        return result
