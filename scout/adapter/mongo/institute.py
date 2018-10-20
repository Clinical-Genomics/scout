import logging

from datetime import datetime
from pprint import pprint as pp

import pymongo

from scout.exceptions import IntegrityError
from scout.constants import PHENOTYPE_GROUPS

LOG = logging.getLogger(__name__)


class InstituteHandler(object):

    def add_institute(self, institute_obj):
        """Add a institute to the database

            Args:
                institute_obj(Institute)
        """
        internal_id = institute_obj['internal_id']
        display_name = institute_obj['internal_id']

        # Check if institute already exists
        if self.institute(institute_id=internal_id):
            raise IntegrityError("Institute {0} already exists in database"
                                 .format(display_name))

        LOG.info("Adding institute with internal_id: {0} and "
                    "display_name: {1}".format(internal_id,
                                               display_name))

        insert_info = self.institute_collection.insert_one(institute_obj)
        ##TODO check if insert info was ok
        LOG.info("Institute saved")

    def update_institute(self, internal_id, sanger_recipient=None, coverage_cutoff=None, 
                         frequency_cutoff=None, display_name=None, remove_sanger=None,
                         phenotype_groups=None, group_abbreviations=None, add_groups=None):
        """Update the information for an institute

        Args:
            internal_id(str): The internal institute id
            sanger_recipient(str): Email adress to add for sanger order
            coverage_cutoff(int): Update coverage cutoff
            frequency_cutoff(float): New frequency cutoff
            display_name(str): New display name
            remove_sanger(str): Email adress for sanger user to be removed
            phenotype_groups(iterable(str)): New phenotype groups
            group_abbreviations(iterable(str))
            add_groups: If groups should be added. If False replace groups
        
        Returns:
            updated_institute(dict)
                     
        """
        add_groups = add_groups or False
        institute_obj = self.institute(internal_id)
        if not institute_obj:
            raise IntegrityError("Institute {} does not exist in database".format(internal_id))
        
        updates = {}
        updated_institute = institute_obj

        if sanger_recipient:
            user_obj = self.user(sanger_recipient)
            if not user_obj:
                raise IntegrityError("user {} does not exist in database".format(sanger_recipient))
                
            LOG.info("Updating sanger recipients for institute: {0} with {1}".format(
                     internal_id, sanger_recipient))
            updates['$push'] = {'sanger_recipients':remove_sanger}

        if remove_sanger:
            LOG.info("Removing sanger recipient {0} from institute: {1}".format(
                     remove_sanger, internal_id))
            updates['$pull'] = {'sanger_recipients':remove_sanger}

        if coverage_cutoff:
            LOG.info("Updating coverage cutoff for institute: {0} to {1}".format(
                            internal_id, coverage_cutoff))
            updates['$set'] = {'coverage_cutoff': coverage_cutoff}
        
        if frequency_cutoff:
            LOG.info("Updating frequency cutoff for institute: {0} to {1}".format(
                            internal_id, frequency_cutoff))
            if not '$set' in updates:
                updates['$set'] = {}
            updates['$set'] = {'frequency_cutoff': frequency_cutoff}

        if display_name:
            LOG.info("Updating display name for institute: {0} to {1}".format(
                            internal_id, display_name))
            if not '$set' in updates:
                updates['$set'] = {}
            updates['$set'] = {'display_name': display_name}

        if phenotype_groups:
            if group_abbreviations:
                group_abbreviations = list(group_abbreviations)
            existing_groups = {}
            if add_groups:
                existing_groups = institute_obj.get('phenotype_groups', PHENOTYPE_GROUPS)

            for i,hpo_term in enumerate(phenotype_groups):
                hpo_obj = self.hpo_term(hpo_term)
                if not hpo_obj:
                    raise IntegrityError("Term {} does not exist".format(hpo_term))
                hpo_id = hpo_obj['hpo_id']
                description = hpo_obj['description']
                abbreviation = None
                if group_abbreviations:
                    abbreviation = group_abbreviations[i]
                existing_groups[hpo_term] = {'name': description, 'abbr':abbreviation}
            updates['$set'] = {'phenotype_groups': existing_groups}
        
        if updates:
            if not '$set' in updates:
                updates['$set'] = {}
            
            updates['$set']['updated_at'] = datetime.now()
            
            updated_institute = self.institute_collection.find_one_and_update(
                {'_id':internal_id}, updates, return_document = pymongo.ReturnDocument.AFTER)
            
            LOG.info("Institute updated")
        
        return updated_institute

    def institute(self, institute_id):
        """Featch a single institute from the backend

            Args:
                institute_id(str)

            Returns:
                Institute object
        """
        LOG.debug("Fetch institute {}".format(institute_id))
        institute_obj = self.institute_collection.find_one({
            '_id': institute_id
        })
        if institute_obj is None:
            LOG.debug("Could not find institute {0}".format(institute_id))

        return institute_obj

    def institutes(self, institute_ids=None):
        """Fetch all institutes.
        
        Args:
            institute_ids(list(str))
        
        Returns:
            res(pymongo.Cursor)
        """
        query = {}
        if institute_ids:
            query['_id'] = {'$in': institute_ids}
        LOG.debug("Fetching all institutes")
        return self.institute_collection.find(query)

