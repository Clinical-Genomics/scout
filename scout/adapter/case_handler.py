# -*- coding: utf-8 -*-
import logging
import datetime

from mongoengine import (DoesNotExist, Q)

from scout.models import (Case, GenePanel, Institute, User)
from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the mongo adapter that handles cases and institutes"""

    def add_institute(self, institute_obj):
        """Add a institute to the database

            Args:
                institute_obj(Institute)
        """
        logger.info("Adding institute with internal_id: {0} and "
                    "display_name: {1}".format(institute_obj['internal_id'],
                                               institute_obj['display_name']))
        if self.institute(institute_id=institute_obj['internal_id']):
            raise IntegrityError("Institute {0} already exists in database"
                                 .format(institute_obj['internal_id']))
        institute_obj.save()
        logger.info("Institute saved")

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
        logger.debug("Fetch institute {}".format(institute_id))
        try:
            return Institute.objects.get(internal_id=institute_id)
        except DoesNotExist:
            logger.debug("Could not find institute {0}".format(institute_id))
            return None

    def institutes(self):
        """Fetch all institutes."""
        return Institute.objects()

    def cases(self, collaborator=None, query=None, skip_assigned=False,
              has_causatives=False, reruns=False, finished=False, 
              research_requested=False, is_research=False):
        """Fetches all cases from the backend.

        Args:
            collaborator(str): If collaborator should be considered
            query(dict): If a specific query is used
            skip_assigned(bool)
            has_causatives(bool)

        Yields:
            Cases ordered by date
        """
        logger.debug("Fetch all cases")
        if collaborator:
            logger.debug("Use collaborator {0}".format(collaborator))
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

        if reruns:
            case_query = case_query.filter(rerun_requested=True)

        if finished:
            case_query = case_query.filter(status__in=['solved', 'archived'])

        if research_requested:
            case_query = case_query.filter(research_requested=True)

        if is_research:
            case_query = case_query.filter(is_research=True)

        return case_query.order_by('-updated_at')

    def case(self, institute_id, case_id):
        """Fetches a single case from database

        Args:
            institute_id(str)
            case_id(str)

        Yields:
            A single Case
        """

        logger.debug("Fetch case {0} from institute {1}".format(
            case_id, institute_id))
        try:
            return Case.objects.get((
                (Q(owner=institute_id) | Q(collaborators=institute_id)) &
                Q(display_name=case_id)
            ))
        except DoesNotExist:
            logger.debug("Could not find case {0}".format(case_id))
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
           If the case already exists exception is raised

            Args:
                case_obj(Case)
        """
        existing_case = self.case(
            institute_id = case_obj['owner'],
            case_id = case_obj['display_name']
        )
        if existing_case:
            raise(IntegrityError("Case {0} already exists in database".format(
                                  case_obj['display_name'])))

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
        existing_case['collaborators'] = list(set(case['collaborators'] + existing_case.collaborators))

        logger.debug("Updating individuals")
        existing_case['individuals'] = case['individuals']

        logger.debug("Updating updated_at")
        existing_case['updated_at'] = datetime.datetime.now()

        logger.debug("Updating analysis dates")
        if 'analysis_dates' in existing_case:
            if case['analysis_date'] not in existing_case['analysis_dates']:
                existing_case['analysis_dates'] = (existing_case['analysis_dates'] +
                                          case['analysis_dates'])
        
        logger.debug("Updating rerun requested to False")
        existing_case.rerun_requested = False
        
        existing_case.default_panels = case.default_panels
        existing_case.gene_panels = case.gene_panels
        
        existing_case.genome_build = case.genome_build
        existing_case.genome_version = case.genome_version
        
        existing_case.rank_model_version = case.rank_model_version
        
        existing_case.madeline_info = case.madeline_info
        
        existing_case.vcf_files = case.vcf_files
        
        existing_case.has_svvariants = case.has_svvariants
        
        existing_case.save()

        ##TODO Add event for updating case?

        return existing_case

    def gene_panel(self, panel_id=None, version=None):
        """Fetch a gene panel.

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel. If 'None' latest version will be returned

        Returns:
            GenePanel: gene panel object
        """
        if version:
            if not panel_id:
                raise SyntaxError("Please provide a panel id")
            try:
                logger.debug("Fetch gene panel {0}, version {1} from database".format(
                    panel_id, version
                ))
                result = GenePanel.objects.get(panel_name=panel_id, version=version)
            except DoesNotExist:
                result = None
        elif panel_id:
            result = GenePanel.objects(panel_name=panel_id).order_by('-version').first()
        else:
            result = GenePanel.objects()

        return result

    def add_gene_panel(self, panel_obj):
        """Add a gene panel to the database

            Args:
                panel_obj(GenePanel)
        """
        panel_name = panel_obj['panel_name']
        panel_version = panel_obj['version']

        logger.info("loading panel {0}, version {1} to database".format(
            panel_name, panel_version
        ))
        if self.gene_panel(panel_name, panel_version):
            raise IntegrityError("Panel {0} with version {1} already"\
                                 " exist in database".format(
                                 panel_name, panel_version))
        panel_obj.save()
        logger.debug("Panel saved")
