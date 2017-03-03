# -*- coding: utf-8 -*-
import logging
import datetime

from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the pymongo adapter that handles cases and institutes"""

    def cases(self, collaborator=None, query=None, skip_assigned=False,
              has_causatives=False, reruns=False, finished=False,
              research_requested=False, is_research=False, status=False,
              name_query=None):
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
        query = query or {}

        if collaborator:
            logger.debug("Use collaborator {0}".format(collaborator))
            query['collaborators'] = collaborator

        if skip_assigned:
            query['assignee'] = {'$exists': False}

        if has_causatives:
            query['causatives'] = {'$exists': True}

        if reruns:
            query['rerun_requested'] = True

        if status:
            query['status'] = status
        elif finished:
            query['status'] = ['solved', 'archived']

        if research_requested:
            query['research_requested'] = True

        if is_research:
            query['is_research'] = True

        if name_query:
            query['display_name'] = {'$regex': name_query}

        return self.case_collection.find(query).sort('updated_at', -1)

    def update_dynamic_gene_list(self, case, gene_list):
        """Update the dynamic gene list for a case

        Arguments:
            case (Case): The case that should be updated
            gene_list (list): The list of genes that should be added
        """
        self.mongoengine_adapter.update_dynamic_gene_list(
            case=case,
            gene_list=gene_list
        )

    def case(self, case_id=None, institute_id=None, display_name=None):
        """Fetches a single case from database
        
        Use either the _id or combination of institute_id and display_name

        Args:
            case_id(str): _id for a caes
            institute_id(str):
            display_name(str)

        Yields:
            A single Case
        """
        query = {}
        if case_id:
            query['_id'] = case_id
            logger.info("Fetching case %s", case_id)
        else:
            if not (institute_id and display_name):
                raise ValueError("Have to provide both institute_id and display_name")
            logger.info("Fetching case %s institute %s", (display_name, institute_id))
            query['owner'] = institute_id
            query['display_name'] = display_name
        
        return self.case_collection.find_one(query)

    def case_ind(self, ind_id):
        """Fetch cases based on an individual id.
        
        Args:
            ind_id(str)
        
        Returns:
            cases(pymongo.cursor): The cases with a matching ind_id
        """

        return self.case_collection.find({'individuals.disply_name': ind_id})

    def delete_case(self, case_id=None, institute_id=None, display_name=None):
        """Delete a single case from database

        Args:
            institute_id(str)
            case_id(str)

        """
        query = {}
        if case_id:
            query['_id'] = case_id
            logger.info("Deleting case %s", case_id)
        else:
            if not (institute_id and display_name):
                raise ValueError("Have to provide both institute_id and display_name")
            logger.info("Deleting case %s institute %s", (display_name, institute_id))
            query['owner'] = institute_id
            query['display_name'] = display_name

        self.case_collection.delete_one(query)

    def add_case(self, case_obj):
        """Add a case to the database
           If the case already exists exception is raised

            Args:
                case_obj(Case)
        """
        logger.info("Adding case %s to database" % case_obj['case_id'])
        if self.case(case_obj['case_id']):
            raise IntegrityError("Case %s already exists in database" % case_obj['case_id'])

        return self.case_collection.insert_one(case_obj)

    def update_case(self, case_obj):
        """Update a case in the database

            Args:
                case_obj(dict): The new case information
        """
        logger.info("Updating case {0}".format(case_obj['_id']))
        
        self.case_collection.update_one({'_id': case_obj['_id']},
            {
                '$addToSet': {
                    'collaborators': {'$each': case_obj['collaborators']},
                    'analysis_dates': {'$each': case_obj['analysis_dates']},
                },
                '$set': {
                    'individuals': case_obj['individuals'],
                    'updated_at': datetime.datetime.now(),
                    'rerun_requested': False,
                    'panels': case_obj.get('panels', []),
                    'genome_build': case_obj.get('genome_build', '37'),
                    'genome_version': case_obj.get('genome_version'),
                    'rank_model_version': case_obj.get('rank_model_version'),
                    'madeline_info': case_obj.get('madeline_info'),
                    'vcf_files': case_obj.get('vcf_files'),
                    'has_svvariants': case_obj.get('has_svvariants'),
                    'assignee': case_obj.get('assignee'), # Should this really be updated?
                }
            }
        )

        logger.info("Case updated")
        ##TODO Add event for updating case?

