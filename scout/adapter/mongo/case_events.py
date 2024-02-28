import logging
from collections import Counter
from typing import Dict, List, Optional

import pymongo

from scout.constants import CASE_STATUSES, CASE_TAGS

LOG = logging.getLogger(__name__)


class CaseEventHandler(object):
    """Class to handle case events for the mongo adapter"""

    def assign(self, institute, case, user, link):
        """Assign a user to a case.

        This function will create an Event to log that a person has been assigned
        to a case. Also the user will be added to case "assignees".

        Args:
            institute (dict): A institute
            case (dict): A case
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case(dict)
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="assign",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$addToSet": {"assignees": user["_id"]}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def unassign(self, institute, case, user, link, inactivate=False):
        """Unassign a user from a case.

        This function will create an Event to log that a person has been
        unassigned from a case. Also the user will be removed from case
        "assignees".

        Args:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object (Should this be a user id?)
            link (dict): The url to be used in the event
            inactivate(bool): inactivate case if there are no assignees

        Returns:
            updated_case (dict): The updated case
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="unassign",
            subject=case["display_name"],
        )

        # if case is not prioritized and user wishes to inactivate it:
        if case["status"] != "prioritized" and inactivate:
            # flag case as inactive:
            case["status"] = "inactive"

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$pull": {"assignees": user["_id"]}, "$set": {"status": case["status"]}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def update_status(self, institute, case, user, status, link):
        """Update the status of a case.

        This function will create an Event to log that a user have updated the
        status of a case. Also the status of the case will be updated.
        Status could be anyone of:
            ("prioritized", "inactive", "active", "solved", "archived")

        Args:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object
            status (str): The new status of the case
            link (str): The url to be used in the event

        Returns:
            updated_case
        """

        if status not in CASE_STATUSES:
            LOG.warning("Status {0} is invalid".format(status))
            return None

        # assign case to user if user unarchives it
        if case.get("status") == "archived" and status == "active":
            self.assign(institute, case, user, link)

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="status",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"status": status}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_case

    def tag_case(
        self, institute: Dict, case: Dict, user: Dict, tags: List[str], link: str
    ) -> Optional[dict]:
        """Update the status tags of a case.

        This function will create an Event to log that a user have updated the
        status of a case. Also the status of the case will be updated.
        Status tags could be any valid keys of the CASE_TAGS constant, eg
            ("provisional", "diagnostic", "carrier", "upd", "medical attention")
        """

        for tag in tags:
            if tag not in CASE_TAGS.keys():
                LOG.warning("Tag {0} is invalid".format(tag))
                return None

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="tag",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"tags": tags}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_case

    def update_synopsis(self, institute, case, user, link, content=""):
        """Create an Event for updating the synopsis for a case.

            This function will create an Event and update the synopsis for
             a case.

        Args:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object
            link (str): The url to be used in the event
            content (str): The content for what should be added to the synopsis

        Returns:
            updated_case
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="synopsis",
            subject=case["display_name"],
            content=content,
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"synopsis": content}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def archive_case(self, institute, case, user, link):
        """Create an event for archiving a case.

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case (dict)
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="archive",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"status": "archived"}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def remove_variants_event(
        self, institute: dict, case: dict, user: dict, link: str, content: str
    ) -> None:
        """Create an event for the action of deleting variants from a case

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
        """
        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="remove_variants",
            subject=case["display_name"],
            content=content,
        )

    def open_research(self, institute, case, user, link):
        """Create an event for opening the research list a case.

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case(dict)
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="open_research",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"research_requested": True}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def reset_research(self, institute, case, user, link):
        """Reset research request status for a given case

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case(dict)
        """
        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="reset_research",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"research_requested": False}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def case_dismissed_variants(self, institute, case):
        """Collect the id of all dismissed variants for a case

        Args:
            institute (dict): an institute id
            case (dict): a case id

        Returns:
            case_dismissed (list): a list of variant ids
        """
        dismissed_variants = Counter(
            [
                var.get("link").rsplit("/", 1)[1]
                for var in self.case_events_by_verb(
                    category="variant",
                    institute=institute,
                    case=case,
                    verb="dismiss_variant",
                )
            ]
        )
        reset_dismissed_variants = Counter(
            [
                var.get("link").rsplit("/", 1)[1]
                for var in self.case_events_by_verb(
                    category="variant",
                    institute=institute,
                    case=case,
                    verb="reset_dismiss_variant",
                )
            ]
        )
        diff_dismissed = dismissed_variants - reset_dismissed_variants
        return list(diff_dismissed.elements())

    def order_dismissed_variants_reset(self, institute, case, user, link):
        """Register the event associated to a user resetting all dismissed variants.

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case
        """
        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="reset_dismiss_all_variants",
            subject=case["display_name"],
        )

        return self.case_collection.find_one({"_id": case["_id"]})

    def update_rerun_status(self, institute, case, user, link):
        """Update rerun status of a case.

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case
        """
        is_rerun = True
        verb = "rerun"
        if case.get("rerun_requested") is True:
            is_rerun = False
            verb = "rerun_reset"

        if is_rerun is True and case.get("status") == "archived":
            # assign case to user requesting rerun
            self.assign(institute, case, user, link)

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb=verb,
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"rerun_requested": is_rerun}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def monitor(self, institute, case, user, link):
        """Enable rerun monitoring for a case.

        Args:
             institute (dict): An Institute object
             case (dict): Case object
             user (dict): A User object
             link (str): The url to be used in the event

        Return:
             updated_case
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="rerun_monitor",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"rerun_monitoring": True}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def unmonitor(self, institute, case, user, link):
        """Disable rerun monitoring for a case.

        Args:
          institute (dict): An Institute object
          case (dict): Case object
          user (dict): A User object
          link (str): The url to be used in the event

        Return:
          updated_case
        """

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="rerun_unmonitor",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"rerun_monitoring": False}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def share(self, institute, case, collaborator_id, user, link):
        """Share a case with a new institute.

        Args:
            institute (dict): An Institute object
            case (dict): Case object
            collaborator_id (str): A instute id
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case
        """
        if collaborator_id in case.get("collaborators", []):
            raise ValueError(f"{collaborator_id} is already a collaborator.")

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="share",
            subject=collaborator_id,
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$push": {"collaborators": collaborator_id}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def unshare(self, institute, case, collaborator_id, user, link):
        """Revoke access for a collaborator for a case.

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            collaborator_id (str): A instute id
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case

        """
        if collaborator_id not in case["collaborators"]:
            raise ValueError("collaborator doesn't have access to case")

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="unshare",
            subject=collaborator_id,
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$pull": {"collaborators": collaborator_id}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def diagnose(
        self,
        institute: dict,
        case: dict,
        user: dict,
        link: str,
        disease_id: str,
        affected_inds: list = [],
        remove: bool = False,
    ) -> Optional[dict]:
        """Add or remove a diagnose to a case and eventually case individuals."""

        updated_diagnoses = []
        case_diagnoses = case.get("diagnosis_phenotypes") or []

        if remove is True:  # Remove term from case diagnoses list
            for case_dia in case_diagnoses:
                if case_dia.get("disease_id") == disease_id:
                    continue
                updated_diagnoses.append(case_dia)
        else:  # Add new diagnosis term to case diseases list
            disease_obj = self.disease_term(disease_identifier=disease_id)
            if disease_obj is None:
                return
            updated_diagnoses = case_diagnoses
            new_dia = {
                "disease_nr": disease_obj["disease_nr"],
                "disease_id": disease_id,
                "description": disease_obj["description"],
            }
            if affected_inds:
                new_dia["individuals"] = [
                    {
                        "individual_id": ind.split("|")[0],
                        "individual_name": ind.split("|")[1],
                    }
                    for ind in affected_inds
                ]
            updated_diagnoses.append(new_dia)

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$set": {"diagnosis_phenotypes": updated_diagnoses}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        if updated_case:
            self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category="case",
                verb="update_diagnosis",
                subject=case["display_name"],
                content=disease_id,
                individuals=[ind.split("|")[1] for ind in affected_inds],
            )

        return updated_case

    def add_cohort(self, institute, case, user, link, tag):
        """Add a cohort tag to case

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            tag (str): The cohort tag to be added

        Return:
            updated_case(dict)
        """
        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="add_cohort",
            subject=link,
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$addToSet": {"cohorts": tag}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def remove_cohort(self, institute, case, user, link, tag):
        """Remove a cohort tag from case

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            tag (str): The cohort tag to be removed

        Return:
            updated_case(dict)
        """
        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="remove_cohort",
            subject=case["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case["_id"]},
            {"$pull": {"cohorts": tag}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def update_clinical_filter_hpo(
        self, institute_obj, case_obj, user_obj, link, hpo_clinical_filter
    ):
        """Update HPO clinical filter setting for a case.

        Args:
            institute_obj (dict): A Institute object
            case_obj (dict): Case object
            user_obj (dict): A User object
            link (str): The url to be used in the event
            hpo_clinical_filter (bool): Toggle for use of dynamic gene panel in clinical filter.
        Return:
            updated_case(dict)
        """
        self.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=link,
            category="case",
            verb="update_clinical_filter_hpo",
            subject=case_obj["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"hpo_clinical_filter": hpo_clinical_filter}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_case

    def update_case_group_ids(self, institute_obj, case_obj, user_obj, link, group_ids):
        """Sets case group_ids, used to group a small number of cases for similar analysis.

        Args:
            case_id(str): case_id
            group_ids(list(str)): A list of group defining tags for related cases. A case can belong to several groups.
        Returns:
            updated_case(case_obj)
        """

        self.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=link,
            category="case",
            verb="update_case_group_ids",
            subject=case_obj["display_name"],
        )

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"group": group_ids}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_case

    def update_default_panels(self, institute_obj, case_obj, user_obj, link, panel_objs):
        """Update default panels for a case.

        Args:
            institute_obj (dict): A Institute object
            case_obj (dict): Case object
            user_obj (dict): A User object
            link (str): The url to be used in the event
            panel_objs (list(dict)): List of panel objs

        Return:
            updated_case(dict)

        """
        self.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=link,
            category="case",
            verb="update_default_panels",
            subject=case_obj["display_name"],
        )

        panel_ids = [panel["_id"] for panel in panel_objs]

        for existing_panel in case_obj["panels"]:
            if existing_panel["panel_id"] in panel_ids:
                existing_panel["is_default"] = True
            else:
                existing_panel["is_default"] = False

        updated_case = self.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"panels": case_obj["panels"]}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_case
