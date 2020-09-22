import logging
from datetime import datetime

from bson import ObjectId
import pymongo

from scout.constants import CASE_STATUSES, REV_ACMG_MAP

COMMENT_LEVELS = ["global", "specific"]

LOG = logging.getLogger(__name__)

from .case_events import CaseEventHandler
from .variant_events import VariantEventHandler


class EventHandler(CaseEventHandler, VariantEventHandler):
    """Class to handle events for the mongo adapter"""

    def delete_event(self, event_id):
        """Delete a event

        Arguments:
            event_id (str): The database key for the event
        """
        LOG.info("Deleting event{0}".format(event_id))
        if not isinstance(event_id, ObjectId):
            event_id = ObjectId(event_id)
        self.event_collection.delete_one({"_id": event_id})
        LOG.debug("Event {0} deleted".format(event_id))

    def create_event(
        self,
        institute,
        case,
        user,
        link,
        category,
        verb,
        subject,
        level="specific",
        variant=None,
        content=None,
        panel=None,
    ):
        """Create a Event with the parameters given.

        Arguments:
            institute (dict): A institute
            case (dict): A case
            user (dict): A User
            link (str): The url to be used in the event
            category (str): case or variant
            verb (str): What type of event
            subject (str): What is operated on
            level (str): 'specific' or 'global'. Default is 'specific'
            variant (dict): A variant
            content (str): The content of the comment

        Returns:
            event(dict): The inserted event
        """
        variant = variant or {}
        event = dict(
            institute=institute["_id"],
            case=case["_id"],
            user_id=user["_id"],
            user_name=user["name"],
            link=link,
            category=category,
            verb=verb,
            subject=subject,
            level=level,
            variant_id=variant.get("variant_id"),
            content=content,
            panel=panel,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        LOG.debug("Saving Event")
        self.event_collection.insert_one(event)
        LOG.debug("Event Saved")
        return event

    def events(
        self,
        institute,
        case=None,
        variant_id=None,
        level=None,
        comments=False,
        panel=None,
    ):
        """Fetch events from the database.

        Args:
          institute (dict): An institute
          case (dict): A case
          variant_id (str, optional): global variant id
          level (str, optional): restrict comments to 'specific' or 'global'
          comments (bool, optional): restrict events to include only comments
          panel (str): A panel name

        Returns:
            pymongo.Cursor: Query result
        """

        query = {}

        if variant_id:
            if comments:
                # If it's comment-related event collect global and variant-specific comment events
                LOG.debug(
                    "Fetching all comments for institute {0} case {1} variant {2}".format(
                        institute["_id"], case["_id"], variant_id
                    )
                )
                query = {
                    "$or": [
                        {
                            "category": "variant",
                            "variant_id": variant_id,
                            "verb": "comment",
                            "level": "global",
                        },
                        {
                            "category": "variant",
                            "variant_id": variant_id,
                            "institute": institute["_id"],
                            "case": case["_id"],
                            "verb": "comment",
                            "level": "specific",
                        },
                    ]
                }
            else:  # Collect other variant-specific events which are not comments
                query["institute"] = institute["_id"]
                query["category"] = "variant"
                query["variant_id"] = variant_id
                query["case"] = case["_id"]
        else:
            query["institute"] = institute["_id"]
            if panel:
                query["panel"] = panel
            # If no variant_id or panel we know that it is a case level comment
            else:
                query["category"] = "case"

                if case:
                    query["case"] = case["_id"]

                if comments:
                    query["verb"] = "comment"

        return self.event_collection.find(query).sort("created_at", pymongo.DESCENDING)

    def user_events(self, user_obj=None):
        """Fetch all events by a specific user."""
        query = dict(user_id=user_obj["_id"]) if user_obj else dict()
        return self.event_collection.find(query)

    def add_phenotype(
        self, institute, case, user, link, hpo_term=None, omim_term=None, is_group=False
    ):
        """Add a new phenotype term to a case

        Create a phenotype term and event with the given information

        Args:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
            hpo_term (str): A hpo id
            omim_term (str): A omim id
            is_group (bool): is phenotype term a group?

        """
        hpo_results = []
        try:
            if hpo_term:
                hpo_results = [hpo_term]
            elif omim_term:
                LOG.debug("Fetching info for mim term {0}".format(omim_term))
                disease_obj = self.disease_term(omim_term)
                if disease_obj:
                    for hpo_term in disease_obj.get("hpo_terms", []):
                        hpo_results.append(hpo_term)
            else:
                raise ValueError("Must supply either hpo or omim term")
        except ValueError as e:
            ## TODO Should ve raise a more proper exception here?
            raise e

        existing_terms = set(term["phenotype_id"] for term in case.get("phenotype_terms", []))

        updated_case = case
        phenotype_terms = []
        for hpo_term in hpo_results:
            LOG.debug("Fetching info for hpo term {0}".format(hpo_term))
            hpo_obj = self.hpo_term(hpo_term)
            if hpo_obj is None:
                raise ValueError("Hpo term: %s does not exist in database" % hpo_term)

            phenotype_id = hpo_obj["_id"]
            description = hpo_obj["description"]
            if phenotype_id not in existing_terms:
                phenotype_term = dict(phenotype_id=phenotype_id, feature=description)
                phenotype_terms.append(phenotype_term)

                LOG.info(
                    "Creating event for adding phenotype term for case"
                    " {0}".format(case["display_name"])
                )

                self.create_event(
                    institute=institute,
                    case=case,
                    user=user,
                    link=link,
                    category="case",
                    verb="add_phenotype",
                    subject=case["display_name"],
                    content=phenotype_id,
                )

            if is_group:
                updated_case = self.case_collection.find_one_and_update(
                    {"_id": case["_id"]},
                    {
                        "$addToSet": {
                            "phenotype_terms": {"$each": phenotype_terms},
                            "phenotype_groups": {"$each": phenotype_terms},
                        }
                    },
                    return_document=pymongo.ReturnDocument.AFTER,
                )
            else:
                updated_case = self.case_collection.find_one_and_update(
                    {"_id": case["_id"]},
                    {"$addToSet": {"phenotype_terms": {"$each": phenotype_terms}}},
                    return_document=pymongo.ReturnDocument.AFTER,
                )

        LOG.debug("Case updated")
        return updated_case

    def remove_phenotype(self, institute, case, user, link, phenotype_id, is_group=False):
        """Remove an existing phenotype from a case

        Args:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (dict): The url to be used in the event
            phenotype_id (str): A phenotype id

        Returns:
            updated_case(dict)
        """
        LOG.info("Removing HPO term from case {0}".format(case["display_name"]))

        if is_group:
            updated_case = self.case_collection.find_one_and_update(
                {"_id": case["_id"]},
                {
                    "$pull": {
                        "phenotype_terms": {"phenotype_id": phenotype_id},
                        "phenotype_groups": {"phenotype_id": phenotype_id},
                    }
                },
                return_document=pymongo.ReturnDocument.AFTER,
            )

        else:
            updated_case = self.case_collection.find_one_and_update(
                {"_id": case["_id"]},
                {"$pull": {"phenotype_terms": {"phenotype_id": phenotype_id}}},
                return_document=pymongo.ReturnDocument.AFTER,
            )

        LOG.info(
            "Creating event for removing phenotype term {0}"
            " from case {1}".format(phenotype_id, case["display_name"])
        )

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category="case",
            verb="remove_phenotype",
            subject=case["display_name"],
        )

        LOG.debug("Case updated")
        return updated_case

    def comment(
        self,
        institute,
        case,
        user,
        link,
        variant=None,
        content="",
        comment_level="specific",
    ):
        """Add a comment to a variant or a case.

        This function will create an Event to log that a user have commented on
        a variant. If a variant id is given it will be a variant comment.
        A variant comment can be 'global' or specific. The global comments will
        be shown for this variation in all cases while the specific comments
        will only be shown for a specific case.

        Arguments:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object
            content (str): The content of the comment
            comment_level (str): Any one of 'specific' or 'global'.
                                 Default is 'specific'

        Return:
            comment(dict): The comment event that was inserted
        """
        if comment_level not in COMMENT_LEVELS:
            raise SyntaxError("Comment levels can only be in {}".format(",".join(COMMENT_LEVELS)))

        if variant:
            LOG.info(
                "Creating event for a {0} comment on variant {1}".format(
                    comment_level, variant["display_name"]
                )
            )

            comment = self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category="variant",
                verb="comment",
                level=comment_level,
                variant=variant,
                subject=variant["display_name"],
                content=content,
            )

        else:
            LOG.info("Creating event for a comment on case {0}".format(case["display_name"]))

            comment = self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category="case",
                verb="comment",
                subject=case["display_name"],
                content=content,
            )
        return comment

    def update_comment(self, comment_id, new_content, level="specific"):
        """Update a case or variant comment

        Args:
            comment_id(str): id of comment event
            new_content(str): updated content of the comment
            level (str): 'specific' (default) or 'global'

        Returns:
            updated_comment(dict): The comment event that was updated
        """
        updated_comment = self.event_collection.find_one_and_update(
            {"_id": ObjectId(comment_id)},
            {
                "$set": {
                    "content": new_content,
                    "level": level,  # This may change while editing variants comments
                    "updated_at": datetime.now(),
                }
            },
        )
        # create an event to register that user has updated a comment
        event = dict(
            institute=updated_comment["institute"],
            case=updated_comment["case"],
            user_id=updated_comment["user_id"],
            user_name=updated_comment["user_name"],
            link=updated_comment["link"],
            category=updated_comment["category"],
            verb="comment_update",
            subject=updated_comment["subject"],
            level=updated_comment["level"],
            variant_id=updated_comment.get("variant_id", None),
            content=None,
            panel=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.event_collection.insert_one(event)
        return updated_comment

    def comments_reupload(self, old_var, new_var, institute_obj, case_obj):
        """Creates comments for a new variant after variant reupload

        Accepts:
            old_var(Variant): the deleted variant
            new_var(Variant): the new variant replacing old_var
            institute_obj(dict): an institute object
            case_obj(dict): a case object

        Returns:
            new_comments(int): the number of created comments
        """
        new_comments = 0

        if new_var["_id"] == old_var["_id"]:
            return new_comments

        link = "/{0}/{1}/{2}".format(new_var["institute"], case_obj["display_name"], new_var["_id"])

        # collect all comments for the old variant
        comments_query = self.events(
            variant_id=old_var["variant_id"],
            comments=True,
            institute=institute_obj,
            case=case_obj,
        )

        # and create the same comment for the new variant
        for old_comment in comments_query:

            comment_user = self.user(old_comment["user_id"])
            if comment_user is None:
                continue

            updated_comment = self.comment(
                institute=institute_obj,
                case=case_obj,
                user=comment_user,
                link=link,
                variant=new_var,
                content=old_comment.get("content"),
                comment_level=old_comment.get("level"),
            )
            if updated_comment:
                new_comments += 1

        return new_comments
