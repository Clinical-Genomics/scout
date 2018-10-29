# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
import datetime

from pprint import pprint as pp

import pymongo

from scout.parse.case import parse_case
from scout.build.case import build_case
from scout.parse.variant.ids import parse_document_id

from scout.exceptions import IntegrityError, ConfigError

LOG = logging.getLogger(__name__)


class CaseHandler(object):
    """Part of the pymongo adapter that handles cases and institutes"""

    def cases(self, collaborator=None, query=None, skip_assigned=False,
              has_causatives=False, reruns=False, finished=False,
              research_requested=False, is_research=False, status=None,
              phenotype_terms=False, pinned=False, cohort=False, name_query=None):
        """Fetches all cases from the backend.

        Args:
            collaborator(str): If collaborator should be considered
            query(dict): If a specific query is used
            skip_assigned(bool)
            has_causatives(bool)
            reruns(bool)
            finished(bool)
            research_requested(bool)
            is_research(bool)
            status(str)
            phenotype_terms(bool): Fetch all cases with phenotype terms
            pinned(bool): Fetch all cases with pinned variants
            name_query(str): Could be hpo term, user, part of display name, 
                             part of inds or part of synopsis

        Yields:
            Cases ordered by date
        """
        LOG.debug("Fetch all cases")
        query = query or {}

        if collaborator:
            LOG.debug("Use collaborator {0}".format(collaborator))
            query['collaborators'] = collaborator

        if skip_assigned:
            query['assignees'] = {'$exists': False}

        if has_causatives:
            query['causatives'] = {'$exists': True, '$ne': []}

        if reruns:
            query['rerun_requested'] = True

        if status:
            query['status'] = status

        elif finished:
            query['status'] = {'$in': ['solved', 'archived']}

        if research_requested:
            query['research_requested'] = True

        if is_research:
            query['is_research'] = True

        if phenotype_terms:
            query['phenotype_terms'] = {'$exists': True, '$ne': []}

        if pinned:
            query['suspects'] = {'$exists': True, '$ne': []}

        if cohort:
            query['cohorts'] = {'$exists': True, '$ne': []}

        if name_query:
            users = self.user_collection.find({'name': {'$regex': name_query, '$options': 'i'}})
            if users.count() > 0:
                query['assignees'] = {'$in': [user['email'] for user in users]}
            elif name_query.startswith('HP:'):
                LOG.debug("HPO case query")
                query['phenotype_terms.phenotype_id'] = name_query
            elif name_query.startswith('synopsis:'):
                synopsis_query=name_query.replace('synopsis:','')
                query['$text']={'$search':synopsis_query}
            else:
                query['$or'] = [
                    {'display_name': {'$regex': name_query}},
                    {'individuals.display_name': {'$regex': name_query}},
                ]

        LOG.info("Get cases with query {0}".format(query))
        return self.case_collection.find(query).sort('updated_at', -1)

    def nr_cases(self, institute_id=None):
        """Return the number of cases
        
        This function will change when we migrate to 3.7.1
        
        Args:
            collaborator(str): Institute id
        
        Returns:
            nr_cases(int)
        """
        query = {}

        if institute_id:
            query['collaborators'] = institute_id
        
        LOG.debug("Fetch all cases with query {0}".format(query))
        nr_cases = self.case_collection.find(query).count()

        return nr_cases
    

    def update_dynamic_gene_list(self, case, hgnc_symbols=None, hgnc_ids=None,
                                 phenotype_ids=None, build='37'):
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
            hgnc_ids (iterable): A list of hgnc_ids

        Returns:
            updated_case(dict)
        """
        dynamic_gene_list = []
        res = []
        if hgnc_ids:
            LOG.info("Fetching genes by hgnc id")
            res = self.hgnc_collection.find({'hgnc_id': {'$in': hgnc_ids}, 'build': build})
        elif hgnc_symbols:
            LOG.info("Fetching genes by hgnc symbols")
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

        LOG.info("Update dynamic gene panel for: %s", case['display_name'])
        updated_case = self.case_collection.find_one_and_update(
            {'_id': case['_id']},
            {'$set': {'dynamic_gene_list': dynamic_gene_list,
                      'dynamic_panel_phenotypes': phenotype_ids or []}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        LOG.debug("Case updated")
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
            LOG.info("Fetching case %s", case_id)
        else:
            if not (institute_id and display_name):
                raise ValueError("Have to provide both institute_id and display_name")
            LOG.info("Fetching case %s institute %s", display_name, institute_id)
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
            LOG.info("Deleting case %s", case_id)
        else:
            if not (institute_id and display_name):
                raise ValueError("Have to provide both institute_id and display_name")
            LOG.info("Deleting case %s institute %s", display_name, institute_id)
            query['owner'] = institute_id
            query['display_name'] = display_name

        result = self.case_collection.delete_one(query)
        return result

    def load_case(self, config_data, update=False):
        """Load a case into the database

        Check if the owner and the institute exists.

        Args:
            config_data(dict): A dictionary with all the necessary information
            update(bool): If existing case should be updated

        Returns:
            case_obj(dict)
        """
        # Check that the owner exists in the database
        institute_obj = self.institute(config_data['owner'])
        if not institute_obj:
            raise IntegrityError("Institute '%s' does not exist in database" % config_data['owner'])

        # Parse the case information
        parsed_case = parse_case(config=config_data)
        # Build the case object
        case_obj = build_case(parsed_case, self)
        # Check if case exists with old case id
        old_caseid = '-'.join([case_obj['owner'], case_obj['display_name']])
        old_case = self.case(old_caseid)
        if old_case:
            LOG.info("Update case id for existing case: %s -> %s", old_caseid, case_obj['_id'])
            self.update_caseid(old_case, case_obj['_id'])
            update = True

        # Check if case exists in database
        existing_case = self.case(case_obj['_id'])
        if existing_case and not update:
            raise IntegrityError("Case %s already exists in database" % case_obj['_id'])

        files = [
            {'file_name': 'vcf_snv', 'variant_type': 'clinical', 'category': 'snv'},
            {'file_name': 'vcf_sv', 'variant_type': 'clinical', 'category': 'sv'},
            {'file_name': 'vcf_cancer', 'variant_type': 'clinical', 'category': 'cancer'},
            {'file_name': 'vcf_str', 'variant_type': 'clinical', 'category': 'str'}
        ]

        for vcf_file in files:
            try:
                if case_obj['vcf_files'].get(vcf_file['file_name']):
                    variant_type = vcf_file['variant_type']
                    category = vcf_file['category']
                    if update:
                        self.delete_variants(
                            case_id=case_obj['_id'],
                            variant_type=variant_type,
                            category=category
                        )
                    self.load_variants(
                        case_obj=case_obj,
                        variant_type=variant_type,
                        category=category,
                        rank_threshold=case_obj.get('rank_score_threshold', 0),
                    )
                else:
                    LOG.debug("didn't find {}, skipping".format(vcf_file['file_name']))
            except (IntegrityError, ValueError, ConfigError, KeyError) as error:
                LOG.warning(error)

        if existing_case and update:
            self.update_case(case_obj)
        else:
            LOG.info('Loading case %s into database', case_obj['display_name'])
            self._add_case(case_obj)

        return case_obj

    def _add_case(self, case_obj):
        """Add a case to the database
           If the case already exists exception is raised

            Args:
                case_obj(Case)
        """
        if self.case(case_obj['_id']):
            raise IntegrityError("Case %s already exists in database" % case_obj['_id'])

        return self.case_collection.insert_one(case_obj)

    def update_case(self, case_obj):
        """Update a case in the database

        The following will be updated:
            - collaborators: If new collaborators these will be added to the old ones
            - analysis_date: Is updated to the new date
            - analyses: The new analysis date will be added to old runs
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
            - has_strvariants: If there are new strvariants
            - multiqc: If there's an updated multiqc report location

            Args:
                case_obj(dict): The new case information

            Returns:
                updated_case(dict): The updated case information
        """
        # Todo: rename to match the intended purpose

        LOG.info("Updating case {0}".format(case_obj['_id']))
        old_case = self.case_collection.find_one(
            {'_id': case_obj['_id']}
        )
        updated_case = self.case_collection.find_one_and_update(
            {'_id': case_obj['_id']},
            {
                '$addToSet': {
                    'collaborators': {'$each': case_obj['collaborators']},
                    'analyses': {
                        'date': old_case['analysis_date'],
                        'delivery_report': old_case.get('delivery_report')
                    }
                },
                '$set': {
                    'analysis_date': case_obj['analysis_date'],
                    'delivery_report': case_obj.get('delivery_report'),
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
                    'has_strvariants': case_obj.get('has_strvariants'),
                    'is_research': case_obj.get('is_research', False),
                    'research_requested': case_obj.get('research_requested', False),
                    'multiqc': case_obj.get('multiqc'),
                }
            },
            return_document=pymongo.ReturnDocument.AFTER
        )

        LOG.info("Case updated")
        return updated_case

    def replace_case(self, case_obj):
        """Replace a existing case with a new one

        Keeps the object id

        Args:
            case_obj(dict)

        Returns:
            updated_case(dict)
        """
        # Todo: Figure out and describe when this method destroys a case if invoked instead of
        # update_case
        LOG.info("Saving case %s", case_obj['_id'])
        # update updated_at of case to "today"

        case_obj['updated_at'] = datetime.datetime.now(),

        updated_case = self.case_collection.find_one_and_replace(
            {'_id': case_obj['_id']},
            case_obj,
            return_document=pymongo.ReturnDocument.AFTER
        )

        return updated_case

    def update_caseid(self, case_obj, family_id):
        """Update case id for a case across the database.

        This function is used when a case is a rerun or updated for another reason.

        Args:
            case_obj(dict)
            family_id(str): The new family id

        Returns:
            new_case(dict): The updated case object

        """
        new_case = deepcopy(case_obj)
        new_case['_id'] = family_id

        # update suspects and causatives
        for case_variants in ['suspects', 'causatives']:
            new_variantids = []
            for variant_id in case_obj.get(case_variants, []):
                case_variant = self.variant(variant_id)
                if not case_variant:
                    continue
                new_variantid = get_variantid(case_variant, family_id)
                new_variantids.append(new_variantid)
            new_case[case_variants] = new_variantids

        # update ACMG
        for acmg_obj in self.acmg_collection.find({'case_id': case_obj['_id']}):
            LOG.info("update ACMG classification: %s", acmg_obj['classification'])
            acmg_variant = self.variant(acmg_obj['variant_specific'])
            new_specific_id = get_variantid(acmg_variant, family_id)
            self.acmg_collection.find_one_and_update(
                {'_id': acmg_obj['_id']},
                {'$set': {'case_id': family_id, 'variant_specific': new_specific_id}},
            )

        # update events
        institute_obj = self.institute(case_obj['owner'])
        for event_obj in self.events(institute_obj, case=case_obj):
            LOG.info("update event: %s", event_obj['verb'])
            self.event_collection.find_one_and_update(
                {'_id': event_obj['_id']},
                {'$set': {'case': family_id}},
            )

        # insert the updated case
        self.case_collection.insert_one(new_case)
        # delete the old case
        self.case_collection.find_one_and_delete({'_id': case_obj['_id']})
        return new_case


def get_variantid(variant_obj, family_id):
    """Create a new variant id.

    Args:
        variant_obj(dict)
        family_id(str)

    Returns:
        new_id(str): The new variant id
    """
    new_id = parse_document_id(
        chrom=variant_obj['chromosome'],
        pos=str(variant_obj['position']),
        ref=variant_obj['reference'],
        alt=variant_obj['alternative'],
        variant_type=variant_obj['variant_type'],
        case_id=family_id,
    )
    return new_id
