# -*- coding: utf-8 -*-
import logging
import datetime

import pymongo

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
            query['assignees'] = {'$exists': False}

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
            users = self.user_collection.find({'name': {'$regex': name_query, '$options':'i'}})
            if users.count() > 0:
                query['assignees'] = {'$in': [user['email'] for user in users]}
            
            else:
                query['$or'] = [
                    {'display_name': {'$regex': name_query}},
                    {'individuals.display_name': {'$regex': name_query}},
                ]

        return self.case_collection.find(query).sort('updated_at', -1)

    def update_dynamic_gene_list(self, case, hgnc_symbols=None, hgnc_ids=None, build='37'):
        """Update the dynamic gene list for a case

        Adds a list of dictionaries to case['dynamic_gene_list'] that looks like

        {
            hgnc_symbol: str,
            hgnc_id: int,
            description: str
        }

        Arguments:
            case (dict): The case that should be updated
            hgnc_symbols (iterable): A list of hgnc_symbols
            hgnc_symbols (iterable): A list of hgnc_symbols

        Returns:
            updated_case(dict)
        """
        dynamic_gene_list = []
        res = []
        if hgnc_ids:
            logger.info("Fetching genes by hgnc id")
            res = self.hgnc_collection.find(
                {'hgnc_id': { '$in': hgnc_ids }, 'build':build }
            )
        elif hgnc_symbols:
            logger.info("Fetching genes by hgnc symbols")
            res = []
            for symbol in hgnc_symbols:
                for gene_obj in self.gene_by_alias(symbol=symbol, build=build):
                    res.append(gene_obj)

        for gene_obj in res:
            dynamic_gene_list.append(
                {
                    'hgnc_symbol': gene_obj['hgnc_symbol'],
                    'hgnc_id': gene_obj['hgnc_id'],
                    'description': gene_obj['description'],
                }
            )

        logger.info("Updating the dynamic gene list for case {0}".format(
                    case['display_name']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id': case['_id']},
            {'$set': {'dynamic_gene_list': dynamic_gene_list}},
            return_document = pymongo.ReturnDocument.AFTER
        )
        logger.debug("Case updated")
        return updated_case

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
            logger.info("Fetching case %s institute %s" % (display_name, institute_id))
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

        Returns:
            case_obj(dict): The case that was deleted
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

        result = self.case_collection.delete_one(query)
        return result

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

        The following will be updated:
            - collaborators: If new collaborators these will be added to the old ones
            - analysis_date: Is updated to the new date
            - analysis_dates: The new analysis date will be added to analysisi dates
            - individuals: There could be new individuals
            - updated_at: When the case was updated in the database
            - rerun_requested: Is set to False since that is probably what happened
            - panels: The new gene panels are added
            - genome_build: If there is a new genome build
            - genome_version: - || -
            - rank_model_version: If there is a new rank model
            - madeline_info: If there is a new pedigree
            - vcf_files: paths to the new files
            - has_svvariants: If there are new svvariants

            Args:
                case_obj(dict): The new case information

            Returns:
                updated_case(dict): The updated case information
        """
        logger.info("Updating case {0}".format(case_obj['_id']))

        updated_case = self.case_collection.find_one_and_update(
            {'_id': case_obj['_id']},
            {
                '$addToSet': {
                    'collaborators': {'$each': case_obj['collaborators']},
                    'analysis_dates': case_obj['analysis_date'],
                },
                '$set': {
                    'analysis_date': case_obj['analysis_date'],
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
                }
            },
            return_document = pymongo.ReturnDocument.AFTER
        )

        logger.info("Case updated")
        return updated_case
        ##TODO Add event for updating case?

