# -*- coding: utf-8 -*-
import logging

from mongoengine import DoesNotExist, Q

from scout.models import (Case, GenePanel, Institute, User)
from scout.ext.backend.utils import get_gene_panel

logger = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the mongo adapter that handles cases and institutes"""

    def add_institute(self, internal_id, display_name):
        """Add a institute to the database

            Args:
                internal_id(str): The internal id (like cust003)
                display_name(str): The display name for a institute (like CMMS)
        """
        logger.info("Creating institute with internal_id: {0} and"\
                    " display_name: {1}".format(internal_id, display_name))
        institute = Institute(
            internal_id=internal_id,
            display_name=display_name
        )
        institute.save()

    def update_institute(self, internal_id, sanger_recipient=None,
                            coverage_cutoff=None):
        """Update the information for an institute

            Args:
                internal_id(str): The internal institute id
                sanger_recipient(str): Email adress for ordering sanger
                coverage_cutoff(int): Update coverage cutoff
        """
        institute = self.institute(internal_id)
        if institute:
            if sanger_recipient:
                logger.info("Updating sanger recipients for institute"\
                            " {0} with {1}".format(
                                internal_id, sanger_recipient))
                institute.sanger_recipients.append(sanger_recipient)
            if coverage_cutoff:
                logger.info("Updating coverage cutoff for institute"\
                            " {0} with {1}".format(
                                internal_id, coverage_cutoff))
                institute.coverage_cutoff = coverage_cutoff
            institute.save()

    def institute(self, institute_id):
        """Featch a single institute from the backend

            Args:
                institute_id(str)

            Returns:
                Institute object
        """
        logger.info("Fetch institute {}".format(
            institute_id))
        try:
            return Institute.objects.get(internal_id=institute_id)
        except DoesNotExist:
            logger.warning("Could not find institute {0}".format(institute_id))
            return None

    def institutes(self):
        """Fetch all institutes."""
        return Institute.objects
    
    def cases(self, collaborator=None, query=None, skip_assigned=False, has_causatives=False):
        """Fetches all cases from the backend.

        Args:
            collaborator(str): If collaborator should be considered
            query(dict): If a specific query is used
            skip_assigned(bool)
            has_causatives(bool)

        Yields:
            Cases ordered by date
        """
        logger.info("Fetch all cases")
        if collaborator:
            logger.info("Use collaborator {0}".format(collaborator))
            case_query = Case.objects(
                Q(owner=collaborator) | Q(collaborators=collaborator)
            )
        else:
            case_query = Case.objects

        if query:
            # filter if any user names match query
            matching_users = User.objects(name__icontains=query)

            # filter cases by matching display name of case or individuals
            case_query = case_query.filter(
                Q(display_name__icontains=query) |
                Q(individuals__display_name__icontains=query) |
                Q(assignee__in=matching_users)
            )

        if skip_assigned:
            case_query = case_query.filter(assignee__exists=False)

        if has_causatives:
            case_query = case_query.filter(causatives__exists=True)

        return case_query.order_by('-updated_at')

    def case(self, institute_id, case_id):
        """Fetches a single case from database

        Args:
            institute_id(str)
            case_id(str)

        Yields:
            A single Case
        """

        logger.info("Fetch case {0} from institute {1}".format(
            case_id, institute_id))
        try:
            return Case.objects.get((
                (Q(owner=institute_id) | Q(collaborators=institute_id)) &
                Q(display_name=case_id)
            ))
        except DoesNotExist:
            logger.warning("Could not find case {0}".format(case_id))
            return None

    def case_ind(self, ind_id):
        """Fetch a case based on an individual id."""
        case_obj = Case.objects.get(individuals__individual_id=ind_id)
        return case_obj

    def delete_case(self, institute_id, case_id):
        """Delete a single case from database

        Args:
            institute_id(str)
            case_id(str)

        """
        logger.info("Fetch case {0} from institute {1}".format(
            case_id, institute_id))

        case_obj = self.case(institute_id, case_id)
        if case_obj:
            logger.info("Deleting case {0}".format(case_obj.case_id))
            case_obj.delete()
            logger.debug("Case deleted")
            return case_obj
            # TODO Add event for deleting case?
        else:
            logger.warning("Could not find case {0}".format(case_id))
            return None

    def add_case(self, case_obj):
        """Add a case to the database

            Args:
                case_obj(Case)
        """
        logger.info("Adding case {0} to database".format(case_obj.case_id))
        case_obj.save()

    def update_case(self, case):
        """Update a case in the database

            Args:
                case(Case): The new case information
        """
        logger.info("Updating case {0}".format(case.case_id))

        existing_case = self.case(
            institute_id=case.owner,
            case_id=case.display_name
        )

        logger.debug("Updating collaborators")
        case['collaborators'] = list(set(case['collaborators'] + existing_case.collaborators))

        logger.debug("Updating is_research to {0}".format(
            existing_case.is_research))
        case['is_research'] = existing_case['is_research']

        logger.debug("Updating created_at to {0}".format(
            existing_case['created_at']))
        case['created_at'] = existing_case['created_at']

        logger.debug("Updating assignee")
        case['assignee'] = existing_case['assignee']

        logger.debug("Updating suspects")
        case['suspects'] = existing_case['suspects']

        logger.debug("Updating causatives")
        case['causatives'] = existing_case['causatives']

        logger.debug("Updating synopsis")
        case['synopsis'] = existing_case['synopsis']

        logger.debug("Updating status to {0}".format(
            existing_case['status']))
        case['status'] = existing_case['status']

        logger.debug("Updating gender_check to {0}".format(
            existing_case['gender_check']))
        case['gender_check'] = existing_case['gender_check']

        logger.debug("Updating phenotype_terms")
        case['phenotype_terms'] = existing_case['phenotype_terms']

        logger.debug("Updating complete status")
        if 'analysis_checked' in existing_case:
            case['analysis_checked'] = existing_case['analysis_checked']

        logger.debug("Updating analysis dates")
        if 'analysis_dates' in existing_case:
            if case['analysis_date'] not in existing_case['analysis_dates']:
                case['analysis_dates'] = (existing_case['analysis_dates'] +
                                          case['analysis_dates'])

        logger.info("Deleting old case {0}".format(
            existing_case['case_id']))
        existing_case.delete()

        ##TODO Add event for updating case?

        return case

    def gene_panel(self, panel_id, version):
        """Fetch a gene panel.

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel

        Returns:
            GenePanel: gene panel object
        """
        try:
            panel = GenePanel.objects.get(panel_name=panel_id, version=version)
        except DoesNotExist:
            return None
        return panel
