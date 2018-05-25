# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from scout.exceptions import IntegrityError

import pymongo

LOG = logging.getLogger(__name__)

class ClinVarHandler(object):
    """Class to handle clinvar submissions for the mongo adapter"""

    def add_clinvar_submission(self, submission_objs, user, institute, case_id):
        """Add a clinvar submission for a case. A submission consists of one or more variants added to the clinvar collection.

            Args:
                submission_obj(list of objects): The list of submission variant objects created in scout/parse/clinvar/create_clinvar_submission_dict.py
                user(str): A user ID
                institute(str): An institute ID
                case_id(str): A case ID

            Returns:
                result:  list: Successful insert returns a list of documents inserted into the clinvar submissions collection.
                         0: no document is inserted into database because there is at least one variant with that clinvar submission ID.
                         -1: no document is inserted into database because there is at least one variant that is already in the clinvar collection (duplicated _id field)

        """
        LOG.info("Adding a clinvar submission '%s' for case %s", submission_objs[0]['clinvar_submission'], case_id)

        # create one object for each submitted variant:
        ids = []
        for subm_variant in submission_objs:
            subm_variant['user'] = user
            subm_variant['institute'] = institute
            subm_variant['case'] = case_id
            subm_variant['created_at'] = datetime.now()
            ids.append(subm_variant['_id'])

        #if there is any variant with the same submssion id (SUBXXX) in the clinvar collection
        if self.clinvars(submission_id=submission_objs[0]['clinvar_submission']):
            result = 0
        elif self.clinvars(variant_ids=ids): #if the variant is already present in the clinvar collection
            result = -1
        else:
            LOG.info("Adding clinvar submission id: {0}".format(submission_objs[0]['clinvar_submission']))
            result = self.clinvar_collection.insert_many(submission_objs)

        return result

    def clinvars(self, variant_ids=None, case_id=None, submission_id=None):
        """Fetch a list of clinvar submissions by providing either a list of variants_ids, a case_id or a submission_id.
            Args:
                variant ids ([_id])
                case_id
                submission_id

            Returns:
                list of clinvar submissions found for any of these arguments
        """
        query = None

        if variant_ids:
            query = { "_id" : { "$in" : variant_ids }}
            LOG.debug("Fetch clinvar submissions for variant ID: {}".format(variant_ids))
        elif case_id:
            query = { 'case' : case_id }
            LOG.debug("Fetch clinvar submissions for case ID: {}".format(case_id))
        else:
            query = {'clinvar_submission': submission_id}
            LOG.debug("Fetch clinvar submissions for submission ID: {}".format(submission_id))

        submission_objs = [ subm for subm in self.clinvar_collection.find( query ).sort('clinvar_submission',pymongo.DESCENDING)]

        if len(submission_objs) == 0:
            LOG.debug("Could not find any clinvar submission for the specified parameters!")
            return None
        else:
            return submission_objs


    def add_clinvar_accession(self, variant_id, clinvar_accession):
        """Introduces the field 'clinvar accession' to a variant submitted to clinvar

            Args:
                variant_ids(str)

            Returns: the submission

        """
        LOG.debug("introducing a clinvar accession for clinvar variant {}".format(variant_id))
        new_doc = self.clinvar_collection.find_one_and_update( {"_id": variant_id}, {"$set": {"clinvar_accession": clinvar_accession}}, return_document=pymongo.ReturnDocument.AFTER )
        return new_doc


    def delete_clinvar_submission(self, submission_id):
        """Delete a series of variants submitted to clinvar matching a submission id

            Args:
                clinvar_id(str)

            Returns: the number of deleted variants

        """
        LOG.debug("Delete clinvar variants with clinvar submissoon id {}".format(submission_id))
        result = self.clinvar_collection.delete_many( {'clinvar_submission': submission_id} )
        return result.deleted_count
