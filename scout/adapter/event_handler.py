import logging

from mongoengine import Q
import phizz

from scout.models import Event, PhenotypeTerm
from scout.compat import reduce

logger = logging.getLogger(__name__)


class EventHandler(object):
    """Class to handle events for the mongo adapter"""

    def delete_event(self, event_id):
        """Delete a event

            Arguments:
                event_id (str): The database key for the event
        """
        logger.info("Deleting event{0}".format(event_id))
        Event.objects(id=event_id).delete()
        logger.debug("Event {0} deleted".format(event_id))

    def create_event(self, institute, case, user, link, category, verb,
                     subject, level='specific', variant_id="", content=""):
        """Create an Event with the parameters given.

        Arguments:
            institute (Institute): A Institute object
            case (Case): A Case object
            user (User): A User object
            link (str): The url to be used in the event
            category (str): Case or Variant
            verb (str): What type of event
            subject (str): What is operated on
            level (str): 'specific' or 'global'. Default is 'specific'
            variant (Variant): A variant object
            content (str): The content of the comment
        """
        event = Event(
            institute=institute,
            case=case,
            author=user.to_dbref(),
            link=link,
            category=category,
            verb=verb,
            subject=subject,
            level=level,
            variant_id=variant_id,
            content=content
        )

        logger.debug("Saving Event")
        event.save()
        logger.debug("Event Saved")

    def events(self, institute, case=None, variant_id=None, level=None,
                comments=False):
        """Fetch events from the database.

          Args:
              institute (Institute): a institute object
              case (Case, optional): case object
              variant_id (str, optional): global variant id
              level (str, optional): restrict comments to 'specific' or 'global'
              comments (bool, optional): restrict events to include only comments

          Returns:
              list: filtered query returning matching events
        """
        # add basic filters
        filters = [Q(institute=institute)]

        if variant_id:
            # restrict to only variant events
            filters.append(Q(category='variant'))
            filters.append(Q(variant_id=variant_id))

            if level:
                # filter on specific/global (implicit: only comments)
                filters.append(Q(level=level))

                if level != 'global':
                    # restrict to case
                    filters.append(Q(case=case))
            else:
                # return both global and specific comments for the variant
                filters.append(Q(case=case) | Q(level='global'))
        else:
            # restrict to case events
            filters.append(Q(category='case'))

            if case:
                # restrict to case only
                filters.append(Q(case=case))

        if comments:
            # restrict events to only comments
            filters.append(Q(verb='comment'))

        query = reduce(lambda old_filter, next_filter: old_filter & next_filter, filters)
        return Event.objects.filter(query)

    def assign(self, institute, case, user, link):
        """Assign a user to a case.

        This function will create an Event to log that a person has been assigned
        to a case. Also the "assignee" on the case will be updated.

        Arguments:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
        """
        logger.info("Creating event for assigning {0} to {1}"
                    .format(user.name.encode('utf-8'), case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='assign',
            subject=case.display_name
        )
        logger.info("Updating {0} to be assigned with {1}"
                    .format(case.display_name, user.name.encode('utf-8')))

        case.assignee = user.to_dbref()
        case.save()
        logger.debug("Case updated")

    def unassign(self, institute, case, user, link):
        """Unassign a user from a case.

        This function will create an Event to log that a person has been
        unassigned from a case. Also the "assignee" on the case will be
        updated.

        Arguments:
            institute (Institute): A Institute object
            case (Case): A Case object
            user (User): A User object (Should this be a user id?)
            link (str): The url to be used in the event
        """
        logger.info("Creating event for unassigning {0} from {1}".format(
                    user.display_name, case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='unassign',
            subject=case.display_name
        )

        logger.info("Updating {0} to be unassigned with {1}".format(
                    case.display_name, user.display_name))

        case.assignee = None
        case.save()
        logger.debug("Case updated")

    def update_status(self, institute, case, user, status, link):
        """Update the status of a case.

        This function will create an Event to log that a user have updated the
        status of a case. Also the status of the case will be updated.

        Arguments:
            institute (Institute): A Institute object
            case (Case): A Case object
            user (User): A User object
            status (str): The new status of the case
            link (str): The url to be used in the event
        """

        logger.info("Creating event for updating status of {0} to {1}".format(
                    case.display_name, status))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='status',
            subject=case.display_name
        )

        logger.info("Updating {0} to status {1}".format(case.display_name, status))
        case.status = status
        case.save()
        logger.debug("Case updated")

    def update_synopsis(self, institute, case, user, link, content=""):
        """Create an Event for updating the synopsis for a case.

            This function will create an Event and update the synopsis for
             a case.

        Arguments:
            institute (Institute): A Institute object
            case (Case): A Case object
            user (User): A User object
            link (str): The url to be used in the event
            content (str): The content for what should be added to the synopsis
        """
        logger.info("Creating event for updating the synopsis for case"\
                    " {0}".format(case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='synopsis',
            subject=case.display_name,
            content=content
        )

        logger.info("Updating the synopsis for case {0}".format(
                    case.display_name))
        case.synopsis = content
        case.save()
        logger.debug("Case updated")

    def archive_case(self, institute, case, user, link):
        """Create an event for archiving a case.

        Arguments:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
        """
        logger.info("Creating event for archiving case {0}".format(
                    case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='archive',
            subject=case.display_name,
        )

        logger.info("Change status for case {0} to 'archived'".format(
                    case.display_name))

        case.status = 'archived'
        case.save()
        logger.debug("Case updated")

    def open_research(self, institute, case, user, link):
        """Create an event for opening the research list a case.

            Arguments:
                institute (Institute): A Institute object
                case (Case): Case object
                user (User): A User object
                link (str): The url to be used in the event
        """
        logger.info("Creating event for opening research for case"
                    " {0}".format(case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='open_research',
            subject=case.display_name,
        )

        case.research_requested = True
        case.save()

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
        try:
            if hpo_term:
                logger.debug("Fetching info for hpo term {0}".format(hpo_term))
                hpo_results = phizz.query_hpo([hpo_term])
            elif omim_term:
                logger.debug("Fetching info for mim term {0}".format(omim_term))
                hpo_results = phizz.query_disease([omim_term])
            else:
                raise ValueError('Must supply either hpo or omim term')
            logger.debug("Got result {0}".format(
                         ', '.join(res['hpo_term'] for res in hpo_results)))
        except ValueError as e:
            # TODO Should ve raise a more proper exception here?
            raise e

        existing_terms = set(term.phenotype_id for term in
                             case.phenotype_terms)
        for hpo_result in hpo_results:
            phenotype_name = hpo_result['hpo_term']
            description = hpo_result['description']
            phenotype_term = PhenotypeTerm(phenotype_id=phenotype_name,
                                           feature=description)
            if phenotype_term.phenotype_id not in existing_terms:
                logger.info("Append the phenotype term {0} to case {1}"
                            .format(phenotype_name, case.display_name))
                case.phenotype_terms.append(phenotype_term)

                logger.info("Creating event for adding phenotype term for case"
                            " {0}".format(case.display_name))

                self.create_event(
                    institute=institute,
                    case=case,
                    user=user,
                    link=link,
                    category='case',
                    verb='add_phenotype',
                    subject=case.display_name,
                    content=phenotype_name
                )
            if is_group:
                existing_groups = set(term.phenotype_id for term in
                                      case.phenotype_groups)
                if phenotype_term.phenotype_id not in existing_groups:
                    logger.info("Append the phenotype group {0} to case {1}"
                                .format(phenotype_name, case.display_name))
                    case.phenotype_groups.append(phenotype_term)

        case.save()
        logger.debug("Case updated")

    def remove_phenotype(self, institute, case, user, link, phenotype_id,
                         is_group=False):
        """Remove an existing phenotype from a case

        Args:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
            phenotype_id (str): A phenotype id
        """
        logger.info("Removing HPO term from case {0}".format(case.display_name))

        if is_group:
            terms = case.phenotype_groups
        else:
            terms = case.phenotype_terms
        for phenotype in terms:
            if phenotype.phenotype_id == phenotype_id:
                terms.remove(phenotype)
                logger.info("Creating event for removing phenotype term {0}"\
                            " from case {1}".format(
                                phenotype_id, case.display_name))

                self.create_event(
                    institute=institute,
                    case=case,
                    user=user,
                    link=link,
                    category='case',
                    verb='remove_phenotype',
                    subject=case.display_name
                )
                break

        case.save()
        logger.debug("Case updated")

    def comment(self, institute, case, user, link, variant=None,
                content="", comment_level="specific"):
        """Add a comment to a variant or a case.

        This function will create an Event to log that a user have commented on
        a variant. If a variant id is given it will be a variant comment.
        A variant comment can be 'global' or specific. The global comments will
        be shown for this variation in all cases while the specific comments
        will only be shown for a specific case.

        Arguments:
            institute (Institute): A Institute object
            case (Case): A Case object
            user (User): A User object
            link (str): The url to be used in the event
            variant (Variant): A variant object
            content (str): The content of the comment
            comment_level (str): Any one of 'specific' or 'global'.
                                 Default is 'specific'
        """
        if variant:
            logger.info("Creating event for a {0} comment on variant {1}".format(
                        comment_level, variant.display_name))

            self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category='variant',
                verb='comment',
                level=comment_level,
                variant_id=variant.variant_id,
                subject=variant.display_name,
                content=content
            )

        else:
            logger.info("Creating event for a comment on case {0}".format(
                        case.display_name))

            self.create_event(
                institute=institute,
                case=case,
                user=user,
                link=link,
                category='case',
                verb='comment',
                subject=case.display_name,
                content=content
            )

    def pin_variant(self, institute, case, user, link, variant):
        """Create an event for pinning a variant.

        Arguments:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
            variant (Variant): A variant object

        """
        logger.info("Creating event for pinning variant {0}".format(
                    variant.display_name))

        # add variant to list of pinned references in the case model
        case.suspects.append(variant)
        case.save()

        kwargs = dict(
            institute=institute,
            case=case,
            user=user,
            link=link,
            verb='pin',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )
        self.create_event(category='variant', **kwargs)
        self.create_event(category='case', **kwargs)

    def unpin_variant(self, institute, case, user, link, variant):
        """Create an event for unpinning a variant.

          Arguments:
              institute (Institute): A Institute object
              case (Case): Case object
              user (User): A User object
              link (str): The url to be used in the event
              variant (Variant): A variant object
        """

        logger.info("Creating event for unpinning variant {0}".format(
                    variant.display_name))

        logger.info("Remove variant from list of references in the case"\
                    " model")
        case.suspects.remove(variant)
        case.save()

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='unpin',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

    def order_sanger(self, institute, case, user, link, variant):
        """Create an event for order sanger for a variant

          Arguments:
              institute (Institute): A Institute object
              case (Case): Case object
              user (User): A User object
              link (str): The url to be used in the event
              variant (Variant): A variant object
        """

        logger.info("Creating event for ordering sanger for variant"\
                    " {0}".format(variant.display_name))

        variant.sanger_ordered = True
        variant.save()

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='sanger',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

        logger.info("Creating event for ordering sanger for case"\
                    " {0}".format(case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='sanger',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

    def validate(self, institute, case, user, link, variant, validate_type):
        """Mark validation status for a variant."""
        variant.validation = validate_type
        variant.save()

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='validate',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

    def mark_causative(self, institute, case, user, link, variant):
        """Create an event for marking a variant causative.

          Arguments:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
            variant (Variant): A variant object
        """
        display_name = variant.display_name
        logger.info("Mark variant {0} as causative in the case {1}".format(
                    display_name, case.display_name))

        logger.info("Adding variant to causatives in case {0}".format(
                    case.display_name))
        case.causatives.append(variant)

        logger.info("Marking case {0} as solved".format(
                    case.display_name))
        case.status = 'solved'
        # persist changes
        case.save()

        logger.info("Creating case event for marking {0}"\
                    " causative".format(variant.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='mark_causative',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

        logger.info("Creating variant event for marking {0}"\
                    " causative".format(case.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='mark_causative',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

    def unmark_causative(self, institute, case, user, link, variant):
        """Create an event for unmarking a variant causative

          Arguments:
              institute (Institute): A Institute object
              case (Case): Case object
              user (User): A User object
              link (str): The url to be used in the event
              variant (Variant): A variant object

        """
        display_name = variant.display_name
        logger.info("Remove variant {0} as causative in case {1}".format(
                    display_name, case.display_name))

        case.causatives.remove(variant)

        # mark the case as active again
        if len(case.causatives) == 0:
            logger.info("Marking case as 'active'")
            case.status = 'active'

        # persist changes
        case.save()

        logger.info("Creating events for unmarking variant {0} "\
                    "causative".format(display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='case',
            verb='unmark_causative',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='unmark_causative',
            variant_id=variant.variant_id,
            subject=variant.display_name,
        )

    def update_manual_rank(self, institute, case, user, link, variant,
                              manual_rank):
        """Create an event for updating the manual rank of a variant

          This function will create a event and update the manual rank
          of the variant.

          Arguments:
          institute (Institute): A Institute object
          case (Case): Case object
          user (User): A User object
          link (str): The url to be used in the event
          variant (Variant): A variant object
          manual_rank (int): The new manual rank

        """
        logger.info("Creating event for updating the manual rank for "\
                    "variant {0}".format(variant.display_name))

        self.create_event(
            institute=institute,
            case=case,
            user=user,
            link=link,
            category='variant',
            verb='manual_rank',
            variant_id=variant.variant_id,
            subject=variant.display_name,
          )
        logger.info("Setting manual rank to {0} for variant {1}".format(
              manual_rank, variant.display_name))
        variant.manual_rank = manual_rank
        variant.save()
        logger.debug("Variant updated")

    def mark_checked(self, institute_model, case_model, user_model, link,
                     unmark=False):
        """Mark a case as checked from an analysis point of view."""
        logger.info("Updating checked status of {}"
                    .format(case_model.display_name))

        status = 'not checked' if unmark else 'checked'
        self.create_event(
            institute=institute_model,
            case=case_model,
            user=user_model,
            link=link,
            category='case',
            verb='check_case',
            subject=status
        )

        logger.info("Updating {0}'s checked status {1}"
                    .format(case_model.display_name, status))
        case_model.analysis_checked = False if unmark else True
        case_model.save()
        logger.debug("Case updated")

    def request_rerun(self, institute_model, case_model, user_model, link):
        """Request a case to be re-analyzed."""
        if case_model.rerun_requested:
            raise ValueError('rerun already pending')

        self.create_event(
            institute=institute_model,
            case=case_model,
            user=user_model,
            link=link,
            category='case',
            verb='rerun',
            subject=case_model.display_name
        )

        case_model.rerun_requested = True
        case_model.save()

    # def update_case(self, institute_model, case_model, link):
    #     """Request a case to be re-analyzed."""
    #
    #     self.create_event(
    #         institute=institute_model,
    #         case=case_model,
    #         link=link,
    #         category='case',
    #         verb='rerun',
    #         subject=case_model.display_name
    #     )
    #
    #     case_model.rerun_requested = True
    #     case_model.save()

    def share(self, institute_model, case_model, collaborator_id,
              user_model, link):
        """Share a case with a new institute."""
        if collaborator_id in case_model.collaborators:
            raise ValueError('new customer is already a collaborator')

        self.create_event(
            institute=institute_model,
            case=case_model,
            user=user_model,
            link=link,
            category='case',
            verb='share',
            subject=collaborator_id
        )

        case_model.collaborators.append(collaborator_id)
        case_model.save()

    def unshare(self, institute_model, case_model, collaborator_id,
                user_model, link):
        """Revoke access for a collaborator for a case."""
        if collaborator_id not in case_model.collaborators:
            raise ValueError("collaborator doesn't have access to case")

        self.create_event(
            institute=institute_model,
            case=case_model,
            user=user_model,
            link=link,
            category='case',
            verb='unshare',
            subject=collaborator_id
        )

        case_model.collaborators.remove(collaborator_id)
        case_model.save()

    def diagnose(self, institute, case_model, current_user, link, level,
                 omim_id, remove=False):
        """Diagnose a case using OMIM ids."""
        if level == 'phenotype':
            diagnosis_list = case_model.diagnosis_phenotypes
        elif level == 'gene':
            diagnosis_list = case_model.diagnosis_genes
        else:
            raise TypeError('wrong level')

        omim_number = int(omim_id.split(':')[-1])
        if remove and omim_number in diagnosis_list:
            diagnosis_list.remove(omim_number)
        elif omim_number not in diagnosis_list:
            diagnosis_list.append(omim_number)

        self.create_event(
            institute=institute,
            case=case_model,
            user=current_user,
            link=link,
            category='case',
            verb='update_diagnosis',
            subject=case_model.display_name,
            content=omim_id
        )

        case_model.save()
        return case_model
