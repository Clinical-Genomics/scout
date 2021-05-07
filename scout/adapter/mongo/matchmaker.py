# -*- coding: utf-8 -*-
import logging
from datetime import datetime

LOG = logging.getLogger(__name__)


class MMEHandler(object):
    """Class to handle case submissions to MatchMaker Exchange"""

    def case_mme_update(self, case_obj, user_obj, mme_subm_obj):
        """Updates a case after a submission to MatchMaker Exchange
        Args:
            case_obj(dict): a scout case object
            user_obj(dict): a scout user object
            mme_subm_obj(dict): contains MME submission params and server response
        Returns:
            updated_case(dict): the updated scout case
        """
        created = None
        patient_ids = []
        updated = datetime.now()
        created = updated

        existing_mm_submission = case_obj.get("mme_submission")
        if existing_mm_submission:
            created = existing_mm_submission.get("created_at")

        patients = [resp["patient"] for resp in mme_subm_obj.get("server_responses")]

        subm_obj = {
            "created_at": created,
            "updated_at": updated,
            "patients": patients,  # list of submitted patient data
            "subm_user": user_obj["_id"],  # submitting user
            "sex": mme_subm_obj["sex"],
            "features": mme_subm_obj["features"],
            "disorders": mme_subm_obj["disorders"],
            "genes_only": mme_subm_obj["genes_only"],
        }
        case_obj["mme_submission"] = subm_obj
        updated_case = self.update_case(case_obj, keep_date=True)

        # create events for subjects add in MatchMaker for this case
        institute_obj = self.institute(case_obj["owner"])
        for individual in case_obj["individuals"]:
            if individual["phenotype"] == 2:  # affected
                # create event for patient
                self.create_event(
                    institute=institute_obj,
                    case=case_obj,
                    user=user_obj,
                    link="",
                    category="case",
                    verb="mme_add",
                    subject=individual["display_name"],
                    level="specific",
                )

        return updated_case

    def case_mme_delete(self, case_obj, user_obj):
        """Delete a MatchMaker submission from a case record
           and creates the related event.
        Args:
            case_obj(dict): a scout case object
            user_obj(dict): a scout user object
        Returns:
            updated_case(dict): the updated scout case

        """
        institute_obj = self.institute(case_obj["owner"])
        # create events for subjects removal from Matchmaker this cas
        for individual in case_obj["individuals"]:
            if individual["phenotype"] == 2:  # affected
                # create event for patient removal
                self.create_event(
                    institute=institute_obj,
                    case=case_obj,
                    user=user_obj,
                    link="",
                    category="case",
                    verb="mme_remove",
                    subject=individual["display_name"],
                    level="specific",
                )

        # Reset mme_submission field for this case
        case_obj["mme_submission"] = None
        updated_case = self.update_case(case_obj, keep_date=True)
        return updated_case
