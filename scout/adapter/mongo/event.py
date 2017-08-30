import logging
from datetime import datetime

from bson import ObjectId
import pymongo

from scout.constants import CASE_STATUSES, REV_ACMG_MAP

logger = logging.getLogger(__name__)


class EventHandler(object):
    """Class to handle events for the mongo adapter"""

    def delete_event(self, event_id):
        """Delete a event

            Arguments:
                event_id (str): The database key for the event
        """
        logger.info("Deleting event{0}".format(event_id))
        if not isinstance(event_id, ObjectId):
            event_id = ObjectId(event_id)
        self.event_collection.delete_one({'_id': event_id})
        logger.debug("Event {0} deleted".format(event_id))

    def create_event(self, institute, case, user, link, category, verb,
                     subject, level='specific', variant=None, content=None,
                     panel=None):
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
        """
        variant = variant or {}
        event = dict(
            institute=institute['_id'],
            case=case['_id'],
            user_id=user['_id'],
            user_name=user['name'],
            link=link,
            category=category,
            verb=verb,
            subject=subject,
            level=level,
            variant_id=variant.get('variant_id'),
            content=content,
            panel=panel,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        logger.debug("Saving Event")
        self.event_collection.insert_one(event)
        logger.debug("Event Saved")

    def events(self, institute, case=None, variant_id=None, level=None,
                comments=False, panel=None):
        """Fetch events from the database.

          Args:
            institute (dict): A institute
            case (dict): A case
            variant_id (str, optional): global variant id
            level (str, optional): restrict comments to 'specific' or 'global'
            comments (bool, optional): restrict events to include only comments
            panel (str): A panel name

          Returns:
              list: filtered query returning matching events
        """

        query = {'institute': institute['_id']}

        if variant_id:
            query['category'] = 'variant'
            query['variant_id'] = variant_id
            if level:
                query['level'] = level
                if level != 'global':
                    query['case'] = case['_id']
        elif panel:
            query['panel'] = panel
        # If no variant_id or panel we know that it is a case level comment
        else:
            query['category'] = 'case'

            if case:
                query['case'] = case['_id']

        if comments:
            query['verb'] = 'comment'

        return self.event_collection.find(query).sort('created_at', pymongo.DESCENDING)

    def user_events(self, user_obj=None):
        """Fetch all events by a specific user."""
        query = dict(user_id=user_obj['_id']) if user_obj else dict()
        return self.event_collection.find(query)

    def assign(self, institute, case, user, link):
        """Assign a user to a case.

        This function will create an Event to log that a person has been assigned
        to a case. Also the user will be added to case "assignees".

        Arguments:
            institute (dict): A institute
            case (dict): A case
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case(dict)
        """
        logger.info("Creating event for assigning {0} to {1}"
                    .format(user['name'].encode('utf-8'), case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='assign',
            subject=case['display_name']
        )
        logger.info("Updating {0} to be assigned with {1}"
                    .format(case['display_name'], user['name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id': case['_id']},
            {'$addToSet': {'assignees': user['_id']}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        return updated_case

    def unassign(self, institute, case, user, link):
        """Unassign a user from a case.

        This function will create an Event to log that a person has been
        unassigned from a case. Also the user will be removed from case
        "assignees".

        Arguments:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object (Should this be a user id?)
            link (dict): The url to be used in the event

        Returns:
            updated_case (dict): The updated case
        """
        logger.info("Creating event for unassigning {0} from {1}".format(
                    user['name'], case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='unassign',
            subject=case['display_name']
        )

        logger.info("Updating {0} to be unassigned with {1}".format(
                    case['display_name'], user['name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id': case['_id']},
            {'$pull': {'assignees': user['_id']}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def update_status(self, institute, case, user, status, link):
        """Update the status of a case.

        This function will create an Event to log that a user have updated the
        status of a case. Also the status of the case will be updated.
        Status could be anyone of:
            ("prioritized", "inactive", "active", "solved", "archived")

        Arguments:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object
            status (str): The new status of the case
            link (str): The url to be used in the event

        Returns:
            updated_case
        """

        if status not in CASE_STATUSES:
            logger.warning("Status {0} is invalid".format(status))
            return None

        logger.info("Creating event for updating status of {0} to {1}".format(
                    case['display_name'], status))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='status',
            subject=case['display_name']
        )

        logger.info("Updating {0} to status {1}".format(case['display_name'], status))
        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {'$set': {'status':status}},
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def update_synopsis(self, institute, case, user, link, content=""):
        """Create an Event for updating the synopsis for a case.

            This function will create an Event and update the synopsis for
             a case.

        Arguments:
            institute (dict): A Institute object
            case (dict): A Case object
            user (dict): A User object
            link (str): The url to be used in the event
            content (str): The content for what should be added to the synopsis

        Returns:
            updated_case
        """
        logger.info("Creating event for updating the synopsis for case"\
                    " {0}".format(case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='synopsis',
            subject=case['display_name'],
            content=content
        )

        logger.info("Updating the synopsis for case {0}".format(
                    case['display_name']))
        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {'$set': {'synopsis':content}},
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def archive_case(self, institute, case, user, link):
        """Create an event for archiving a case.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case (dict)
        """
        logger.info("Creating event for archiving case {0}".format(
                    case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='archive',
            subject=case['display_name'],
        )

        logger.info("Change status for case {0} to 'archived'".format(
                    case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {'$set': {'status':'archived'}},
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def open_research(self, institute, case, user, link):
        """Create an event for opening the research list a case.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Returns:
            updated_case(dict)
        """
        logger.info("Creating event for opening research for case"
                    " {0}".format(case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='open_research',
            subject=case['display_name'],
        )

        logger.info("Set research_requested for case {0} to True".format(
                    case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {'$set': {'research_requested':True}},
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def add_phenotype(self, institute, case, user, link, hpo_term=None,
                      omim_term=None, is_group=False):
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
                logger.debug("Fetching info for mim term {0}".format(omim_term))
                disease_obj = self.disease_term(omim_term)
                if disease_obj:
                    for hpo_term in disease_obj.get('hpo_terms', []):
                        hpo_results.append(hpo_term)
            else:
                raise ValueError('Must supply either hpo or omim term')
        except ValueError as e:
            ## TODO Should ve raise a more proper exception here?
            raise e

        existing_terms = set(term['phenotype_id'] for term in
                             case.get('phenotype_terms', []))

        updated_case = case
        phenotype_terms = []
        for hpo_term in hpo_results:
            logger.debug("Fetching info for hpo term {0}".format(hpo_term))
            hpo_obj = self.hpo_term(hpo_term)
            if hpo_obj is None:
                raise ValueError("Hpo term: %s does not exist in database" % hpo_term)

            phenotype_id = hpo_obj['_id']
            description = hpo_obj['description']
            if phenotype_id not in existing_terms:
                phenotype_term = dict(phenotype_id=phenotype_id, feature=description)
                phenotype_terms.append(phenotype_term)

                logger.info("Creating event for adding phenotype term for case"
                            " {0}".format(case['display_name']))

                self.create_event(
                    institute=institute,
                    case=case,
                    user=user,
                    link=link,
                    category='case',
                    verb='add_phenotype',
                    subject=case['display_name'],
                    content=phenotype_id
                )

            if is_group:
                updated_case = self.case_collection.find_one_and_update(
                    {'_id': case['_id']},
                    {
                        '$addToSet': {
                            'phenotype_terms': {'$each': phenotype_terms},
                            'phenotype_groups': {'$each': phenotype_terms},
                        },
                    },
                    return_document=pymongo.ReturnDocument.AFTER
                )
            else:
                updated_case = self.case_collection.find_one_and_update(
                    {'_id': case['_id']},
                    {
                        '$addToSet': {
                            'phenotype_terms': {'$each': phenotype_terms},
                        },
                    },
                    return_document=pymongo.ReturnDocument.AFTER
                )

        logger.debug("Case updated")
        return updated_case

    def remove_phenotype(self, institute, case, user, link, phenotype_id,
                         is_group=False):
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
        logger.info("Removing HPO term from case {0}".format(case['display_name']))

        if is_group:
            updated_case = self.case_collection.find_one_and_update(
                {'_id': case['_id']},
                {
                    '$pull': {
                        'phenotype_terms': {'phenotype_id': phenotype_id},
                        'phenotype_groups': {'phenotype_id': phenotype_id},
                    },
                },
                return_document = pymongo.ReturnDocument.AFTER
            )

        else:
            updated_case = self.case_collection.find_one_and_update(
                {'_id': case['_id']},
                {
                    '$pull': {
                        'phenotype_terms': {'phenotype_id': phenotype_id},
                    },
                },
                return_document = pymongo.ReturnDocument.AFTER
            )

        logger.info("Creating event for removing phenotype term {0}"\
                    " from case {1}".format(phenotype_id, case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='remove_phenotype',
            subject=case['display_name']
        )

        logger.debug("Case updated")
        return updated_case

    def comment(self, institute, case, user, link, variant=None,
                content="", comment_level="specific"):
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
        """
        if variant:
            logger.info("Creating event for a {0} comment on variant {1}".format(
                        comment_level, variant['display_name']))

            self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category='variant',
                verb='comment',
                level=comment_level,
                variant=variant,
                subject=variant['display_name'],
                content=content
            )

        else:
            logger.info("Creating event for a comment on case {0}".format(
                        case['display_name']))

            self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category='case',
                verb='comment',
                subject=case['display_name'],
                content=content
            )

    def pin_variant(self, institute, case, user, link, variant):
        """Create an event for pinning a variant.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object

        Returns:
            updated_case
        """
        logger.info("Creating event for pinning variant {0}".format(
                    variant['display_name']))

        # add variant to list of pinned references in the case model
        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {'$push': {'suspects': variant['_id']}},
            return_document = pymongo.ReturnDocument.AFTER
        )

        kwargs = dict(
            institute=institute,
            case=case,
            user=user,
            link=link,
            verb='pin',
            variant=variant,
            subject=variant['display_name'],
        )
        self.create_event(category='variant', **kwargs)
        self.create_event(category='case', **kwargs)

        return updated_case

    def unpin_variant(self, institute, case, user, link, variant):
        """Create an event for unpinning a variant.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object

        Returns:
            updated_case(dict)
        """
        logger.info("Creating event for unpinning variant {0}".format(
                    variant['display_name']))

        logger.info("Remove variant from list of references in the case"\
                    " model")

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {'$pull': {'suspects': variant['_id']}},
            return_document = pymongo.ReturnDocument.AFTER
        )

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='unpin',
            variant=variant,
            subject=variant['display_name'],
        )

        return updated_case

    def order_sanger(self, institute, case, user, link, variant):
        """Create an event for order sanger for a variant

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object

        Returns:
            updated_variant(dict)
        """
        logger.info("Creating event for ordering sanger for variant"\
                    " {0}".format(variant['display_name']))

        updated_variant = self.variant_collection.find_one_and_update(
            {'_id':variant['_id']},
            {'$set': {'sanger_ordered': True}},
            return_document = pymongo.ReturnDocument.AFTER
        )

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='sanger',
            variant=variant,
            subject=variant['display_name'],
        )

        logger.info("Creating event for ordering sanger for case"\
                    " {0}".format(case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='sanger',
            variant=variant,
            subject=variant['display_name'],
        )
        return updated_variant

    def validate(self, institute, case, user, link, variant, validate_type):
        """Mark validation status for a variant.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object
            validate_type(str): The outcome of validation.
                                choices=('True positive', 'False positive')

        Returns:
            updated_variant(dict)
        """
        if not validate_type in ['True positive', 'False positive']:
            logger.warning("Invalid validation string: %s", validate_type)
            return

        updated_variant = self.variant_collection.find_one_and_update(
            {'_id':variant['_id']},
            {'$set': {'validation': validate_type}},
            return_document = pymongo.ReturnDocument.AFTER
        )

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='validate',
            variant=variant,
            subject=variant['display_name'],
        )
        return updated_variant

    def mark_causative(self, institute, case, user, link, variant):
        """Create an event for marking a variant causative.

        Arguments:
          institute (dict): A Institute object
          case (dict): Case object
          user (dict): A User object
          link (str): The url to be used in the event
          variant (variant): A variant object

        Returns:
            updated_case(dict)
        """
        display_name = variant['display_name']
        logger.info("Mark variant {0} as causative in the case {1}".format(
                    display_name, case['display_name']))

        logger.info("Adding variant to causatives in case {0}".format(
                    case['display_name']))

        logger.info("Marking case {0} as solved".format(
                    case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id': case['_id']},
            {
                '$push': {'causatives': variant['_id']},
                '$set': {'status': 'solved'}
            },
            return_document = pymongo.ReturnDocument.AFTER
        )

        logger.info("Creating case event for marking {0}"\
                    " causative".format(variant['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='mark_causative',
            variant=variant,
            subject=variant['display_name'],
        )

        logger.info("Creating variant event for marking {0}"\
                    " causative".format(case['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='mark_causative',
            variant=variant,
            subject=variant['display_name'],
        )
        return updated_case

    def unmark_causative(self, institute, case, user, link, variant):
        """Create an event for unmarking a variant causative

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object

        Returns:
            updated_case(dict)

        """
        display_name = variant['display_name']
        logger.info("Remove variant {0} as causative in case {1}".format(
                    display_name, case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$pull': {'causatives': variant['_id']},
            },
            return_document = pymongo.ReturnDocument.AFTER
        )

        # mark the case as active again
        if len(updated_case.get('causatives', [])) == 0:
            logger.info("Marking case as 'active'")
            updated_case = self.case_collection.find_one_and_update(
                {'_id':case['_id']},
                {
                    '$set': {'status': 'active'}
                },
                return_document = pymongo.ReturnDocument.AFTER
            )

        logger.info("Creating events for unmarking variant {0} "\
                    "causative".format(display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='unmark_causative',
            variant=variant,
            subject=variant['display_name'],
        )

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='unmark_causative',
            variant=variant,
            subject=variant['display_name'],
        )

        return updated_case

    def update_manual_rank(self, institute, case, user, link, variant,
                              manual_rank):
        """Create an event for updating the manual rank of a variant

          This function will create a event and update the manual rank
          of the variant.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            variant (dict): A variant object
            manual_rank (int): The new manual rank

        Return:
            updated_variant

        """
        logger.info("Creating event for updating the manual rank for "\
                    "variant {0}".format(variant['display_name']))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='manual_rank',
            variant=variant,
            subject=variant['display_name'],
          )
        logger.info("Setting manual rank to {0} for variant {1}".format(
              manual_rank, variant['display_name']))

        updated_variant = self.variant_collection.find_one_and_update(
            {'_id':variant['_id']},
            {'$set': {'manual_rank': manual_rank}},
            return_document = pymongo.ReturnDocument.AFTER
        )

        logger.debug("Variant updated")
        return updated_variant

    def update_acmg(self, institute_obj, case_obj, user_obj, link, variant_obj, acmg_str):
        """Create an event for updating the ACMG classification of a variant.

        Arguments:
            institute_obj (dict): A Institute object
            case_obj (dict): Case object
            user_obj (dict): A User object
            link (str): The url to be used in the event
            variant_obj (dict): A variant object
            acmg_str (str): The new ACMG classification string

        Returns:
            updated_variant
        """
        self.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=link,
            category='variant',
            verb='acmg',
            variant=variant_obj,
            subject=variant_obj['display_name'],
        )
        logger.info("Setting ACMG to {} for: {}".format(acmg_str, variant_obj['display_name']))

        if acmg_str is None:
            updated_variant = self.variant_collection.find_one_and_update(
                {'_id': variant_obj['_id']},
                {'$unset': {'acmg_classification': 1}},
                return_document=pymongo.ReturnDocument.AFTER
            )
        else:
            updated_variant = self.variant_collection.find_one_and_update(
                {'_id': variant_obj['_id']},
                {'$set': {'acmg_classification': REV_ACMG_MAP[acmg_str]}},
                return_document=pymongo.ReturnDocument.AFTER
            )

        logger.debug("Variant updated")
        return updated_variant

    def mark_checked(self, institute, case, user, link,
                     unmark=False):
        """Mark a case as checked from an analysis point of view.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            unmark (bool): If case should ve unmarked

        Return:
            updated_case
        """

        logger.info("Updating checked status of {}"
                    .format(case['display_name']))

        status = 'not checked' if unmark else 'checked'
        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='check_case',
            subject=status
        )

        logger.info("Updating {0}'s checked status {1}"
                    .format(case['display_name'], status))
        analysis_checked = False if unmark else True
        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$set': {'analysis_checked': analysis_checked}
            },
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def request_rerun(self, institute, case, user, link):
        """Request a case to be re-analyzed.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case
        """
        if case.get('rerun_requested'):
            raise ValueError('rerun already pending')

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='rerun',
            subject=case['display_name']
        )

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$set': {'rerun_requested': True}
            },
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def share(self, institute, case, collaborator_id, user, link):
        """Share a case with a new institute.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            collaborator_id (str): A instute id
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case
        """
        if collaborator_id in case.get('collaborators', []):
            raise ValueError('new customer is already a collaborator')

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='share',
            subject=collaborator_id
        )

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$push': {'collaborators': collaborator_id}
            },
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def unshare(self, institute, case, collaborator_id, user, link):
        """Revoke access for a collaborator for a case.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            collaborator_id (str): A instute id
            user (dict): A User object
            link (str): The url to be used in the event

        Return:
            updated_case

        """
        if collaborator_id not in case['collaborators']:
            raise ValueError("collaborator doesn't have access to case")

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='unshare',
            subject=collaborator_id
        )

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$pull': {'collaborators': collaborator_id}
            },
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def diagnose(self, institute, case, user, link, level, omim_id, remove=False):
        """Diagnose a case using OMIM ids.

        Arguments:
            institute (dict): A Institute object
            case (dict): Case object
            user (dict): A User object
            link (str): The url to be used in the event
            level (str): choices=('phenotype','gene')

        Return:
            updated_case

        """
        if level == 'phenotype':
            case_key = 'diagnosis_phenotypes'
        elif level == 'gene':
            case_key = 'diagnosis_genes'
        else:
            raise TypeError('wrong level')

        diagnosis_list = case.get(case_key, [])
        omim_number = int(omim_id.split(':')[-1])

        updated_case = None
        if remove and omim_number in diagnosis_list:
            updated_case = self.case_collection.find_one_and_update(
                {'_id': case['_id']},
                {'$pull': {case_key: omim_number}},
                return_document=pymongo.ReturnDocument.AFTER
            )

        elif omim_number not in diagnosis_list:
            updated_case = self.case_collection.find_one_and_update(
                {'_id': case['_id']},
                {'$push': {case_key: omim_number}},
                return_document=pymongo.ReturnDocument.AFTER
            )

        if updated_case:
            self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category='case',
                verb='update_diagnosis',
                subject=case['display_name'],
                content=omim_id
            )

        return updated_case

    def add_cohort(self, institute, case, user, link, tag):
        """Add a cohort tag to case

        Arguments:
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
            category='case',
            verb='add_cohort',
            subject=link
        )

        logger.info("Adding cohort tag {0} to {1}"
                    .format(tag, case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$addToSet': {'cohorts': tag},
            },
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def remove_cohort(self, institute, case, user, link, tag):
        """Remove a cohort tag from case

        Arguments:
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
            category='case',
            verb='remove_cohort',
            subject=case['display_name'],
        )

        logger.info("Removing cohort tag {0} to {1}"
                    .format(tag, case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id':case['_id']},
            {
                '$pull': {'cohorts': tag},
            },
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

    def update_default_panels(self, institute_obj, case_obj, user_obj, link, panel_objs):
        """Update default panels for a case.

        Arguments:
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
            category='case',
            verb='update_default_panels',
            subject=case_obj['display_name'],
        )

        logger.info("Update default panels for {}".format(case_obj['display_name']))

        panel_ids = [panel['_id'] for panel in panel_objs]

        for existing_panel in case_obj['panels']:
            if existing_panel['panel_id'] in panel_ids:
                existing_panel['is_default'] = True
            else:
                existing_panel['is_default'] = False

        updated_case = self.case_collection.find_one_and_update(
            {'_id': case_obj['_id']},
            {
                '$set': {'panels': case_obj['panels']}
            },
            return_document=pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")

        return updated_case
