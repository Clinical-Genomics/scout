# -*- coding: utf-8 -*-
import logging
from datetime import datetime

LOG = logging.getLogger(__name__)


class MMEHandler(object):
    """Class to handle case submissions to MatchMaker Exchange"""

    def user_mme_submissions(self, user_obj):
        """Return a set of all case _ids submitted to the Matchmaker Exchange by a user.

        Args:
            user_obj(dict): a scout user object
        Returns:
            submitted_cases(set); a set of case _ids
        """
        # All events associated to the provided user
        user_events = self.user_events(user_obj)
        # Collect unique case _id with MME submissions from provided user
        submitted_cases = set()

        for event in user_events:
            if event.get("verb") != "mme_add":
                continue
            # Check that the cases patient's submission are still actual
            CASE_MME_SUBMISSIONS_PROJECTION = {"mme_submission": 1}
            case_obj = self.case(
                case_id=event.get("case"), projection=CASE_MME_SUBMISSIONS_PROJECTION
            )
            if case_obj is None:
                continue
            # Check that the case as an associated MME submission and that the user is the actual patients' contact
            if case_obj.get("mme_submission") is None or case_obj["mme_submission"].get(
                "subm_user"
            ) != user_obj.get("email"):
                continue
            submitted_cases.add(case_obj["_id"])
        return submitted_cases

    def mme_reassign(self, case_ids, new_users_email):
        """Reassign cases submitted to MME to another user
        Args:
            case_ids(set): a set of case _ids
            new_users_email(str): email of another user in Scout
        """
        new_contact = self.user(new_users_email)
        if new_contact is None:
            raise ValueError(f"User with email '{new_users_email}' was not found.")
        if "mme_submitter" not in new_contact.get("roles"):
            raise ValueError(
                f"Scout user with email '{new_users_email}' doesn't have a 'mme_submitter' role."
            )
        # Update MME submissions
        new_patient_contact = {
            "name": new_contact["name"],
            "href": ":".join(["mailto", new_users_email]),
            "institution": "Scout software user, Science For Life Laboratory, Stockholm, Sweden",
        }
        for case_id in case_ids:
            case_obj = self.case(case_id=case_id)
            case_subm_object = case_obj["mme_submission"]
            # Update patients's contact info with new user data
            for patient in case_subm_object.get("patients", []):
                patient["contact"] = new_patient_contact
            updated_case = self.case_mme_update(case_obj, new_contact, case_subm_object)
            if updated_case:
                LOG.info(f"MME contact info updated for case:{updated_case['_id']}")

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
        patients = []

        existing_mm_submission = case_obj.get("mme_submission")
        if existing_mm_submission:
            created = existing_mm_submission.get("created_at")
            patients = existing_mm_submission.get("patients")

        if mme_subm_obj.get("server_responses"):
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
        link = f"/{institute_obj['_id']}/{case_obj['display_name']}"
        for individual in case_obj["individuals"]:
            if individual["phenotype"] == 2:  # affected
                # create event for patient
                self.create_event(
                    institute=institute_obj,
                    case=case_obj,
                    user=user_obj,
                    link=link,
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
        # create events for subjects removal from Matchmaker this case
        link = f"/{institute_obj['_id']}/{case_obj['display_name']}"
        for individual in case_obj["individuals"]:
            if individual["phenotype"] == 2:  # affected
                # create event for patient removal
                self.create_event(
                    institute=institute_obj,
                    case=case_obj,
                    user=user_obj,
                    link=link,
                    category="case",
                    verb="mme_remove",
                    subject=individual["display_name"],
                    level="specific",
                )

        # Reset mme_submission field for this case
        case_obj["mme_submission"] = None
        updated_case = self.update_case(case_obj, keep_date=True)
        return updated_case
