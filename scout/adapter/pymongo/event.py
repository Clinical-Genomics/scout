import logging

logger = logging.getLogger(__name__)


class EventHandler(object):
    """Class to handle events for the mongo adapter"""

    def delete_event(self, event_id):
        """Delete a event

            Arguments:
                event_id (str): The database key for the event
        """
        self.mongoengine_adapter.delete_event(
            event_id = event_id
        )

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
        self.mongoengine_adapter.create_event(
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
        return self.mongoengine_adapter.events(
                institute=institute,
                case=case,
                variant_id=variant_id,
                level=level,
                comments=comments,
                )

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
        self.mongoengine_adapter.assign(
                institute=institute,
                case=case,
                user=user,
                link=link,
                )

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
        self.mongoengine_adapter.unassign(
                institute=institute,
                case=case,
                user=user,
                link=link,
                )

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
        self.mongoengine_adapter.update_status(
                institute=institute,
                case=case,
                user=user,
                status=status,
                link=link,
                )

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
        self.mongoengine_adapter.update_synopsis(
                institute=institute,
                case=case,
                user=user,
                link=link,
                content=content
                )

    def archive_case(self, institute, case, user, link):
        """Create an event for archiving a case.

        Arguments:
            institute (Institute): A Institute object
            case (Case): Case object
            user (User): A User object
            link (str): The url to be used in the event
        """
        self.mongoengine_adapter.archive_case(
                institute=institute,
                case=case,
                user=user,
                link=link,
                )

    def open_research(self, institute, case, user, link):
        """Create an event for opening the research list a case.

            Arguments:
                institute (Institute): A Institute object
                case (Case): Case object
                user (User): A User object
                link (str): The url to be used in the event
        """
        self.mongoengine_adapter.open_research(
                institute=institute,
                case=case,
                user=user,
                link=link,
                )

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
        self.mongoengine_adapter.add_phenotype(
                institute=institute,
                case=case,
                user=user,
                link=link,
                hpo_term=hpo_term,
                omim_term=omim_term,
                is_group=is_group
        )
                      

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
        self.mongoengine_adapter.remove_phenotype(
                institute=institute,
                case=case,
                user=user,
                link=link,
                phenotype_id=phenotype_id,
                is_group=is_group
        )

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
        self.mongoengine_adapter.comment(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
                content=content,
                comment_level=comment_level
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
        self.mongoengine_adapter.pin_variant(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
        )

    def unpin_variant(self, institute, case, user, link, variant):
        """Create an event for unpinning a variant.

          Arguments:
              institute (Institute): A Institute object
              case (Case): Case object
              user (User): A User object
              link (str): The url to be used in the event
              variant (Variant): A variant object
        """
        self.mongoengine_adapter.unpin_variant(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
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
        self.mongoengine_adapter.order_sanger(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
        )


    def validate(self, institute, case, user, link, variant, validate_type):
        """Mark validation status for a variant."""
        self.mongoengine_adapter.validate(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
                validate_type=validate_type,
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
        self.mongoengine_adapter.mark_causative(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
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
        self.mongoengine_adapter.unmark_causative(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
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
        self.mongoengine_adapter.update_manual_rank(
                institute=institute,
                case=case,
                user=user,
                link=link,
                variant=variant,
                manual_rank=manual_rank,
        )


    def mark_checked(self, institute_model, case_model, user_model, link,
                     unmark=False):
        """Mark a case as checked from an analysis point of view."""
        self.mongoengine_adapter.mark_checked(
                institute_model=institute_model,
                case_model=case_model,
                user_model=user_model,
                link=link,
                unmark=unmark,
        )

    def request_rerun(self, institute_model, case_model, user_model, link):
        """Request a case to be re-analyzed."""
        self.mongoengine_adapter.request_rerun(
                institute_model=institute_model,
                case_model=case_model,
                user_model=user_model,
                link=link,
        )


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
        self.mongoengine_adapter.share(
                institute_model=institute_model,
                case_model=case_model,
                user_model=user_model,
                link=link,
                collaborator_id=collaborator_id,
        )


    def unshare(self, institute_model, case_model, collaborator_id,
                user_model, link):
        """Revoke access for a collaborator for a case."""
        self.mongoengine_adapter.unshare(
                institute_model=institute_model,
                case_model=case_model,
                user_model=user_model,
                link=link,
                collaborator_id=collaborator_id,
        )


    def diagnose(self, institute, case_model, current_user, link, level,
                 omim_id, remove=False):
        """Diagnose a case using OMIM ids."""
        return self.mongoengine_adapter.diagnose(
                institute=institute,
                case_model=case_model,
                current_user=current_user,
                link=link,
                level=level,
                omim_id=omim_id,
                remove=remove,
        )

