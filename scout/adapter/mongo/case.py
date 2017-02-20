# -*- coding: utf-8 -*-
import logging
import datetime


logger = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the pymongo adapter that handles cases and institutes"""

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
        return self.mongoengine_adapter.cases(
            collaborator=collaborator, 
            query=query, 
            skip_assigned=skip_assigned,
            has_causatives=has_causatives, 
            reruns=reruns, 
            finished=finished,
            research_requested=research_requested, 
            is_research=is_research
        )
    
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

    def case(self, institute_id, case_id):
        """Fetches a single case from database

        Args:
            institute_id(str)
            case_id(str)

        Yields:
            A single Case
        """
        return self.mongoengine_adapter.case(
            institute_id = institute_id,
            case_id = case_id
        )

    def case_ind(self, ind_id):
        """Fetch a case based on an individual id."""
        return self.mongoengine_adapter.case_ind(ind_id=ind_id)

    def delete_case(self, institute_id, case_id):
        """Delete a single case from database

        Args:
            institute_id(str)
            case_id(str)

        """
        return self.mongoengine_adapter.delete_case(
            institute_id = institute_id,
            case_id = case_id
        )

    def add_case(self, case_obj):
        """Add a case to the database
           If the case already exists exception is raised

            Args:
                case_obj(Case)
        """
        return self.mongoengine_adapter.add_case(case_obj=case_obj)

    def update_case(self, case):
        """Update a case in the database

            Args:
                case(Case): The new case information
        """
        return self.mongoengine_adapter.update_case(case=case)

