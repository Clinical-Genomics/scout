# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from scout.exceptions import IntegrityError

import pymongo

logger = logging.getLogger(__name__)

class ClinVarHandler(object):
    """Class to handle clinvar submissions for the mongo adapter"""

    def add_clinvar_submission(self, submission_obj, user, institute, case):
        """Add a clinvar submission for a case. A submission consists of one or more variants added to the clinvar collection.

            Args:
                submission_obj(dict)
                user_obj(dict)
                institute_obj(dict)
                case_obj(dict)

            Returns:
                number of documents inserted into the clinvar submissions collection (== variants submitted).

        """
        logger.info("Adding a clinvar submission '%s' for case %s", submission_obj[0]['clinvar_submission'], user)

        # create one object for each submitted variant:
        ids = []
        for subm_variant in submission_obj:
            subm_variant['user'] = user
            subm_variant['institute'] = institute
            subm_variant['case'] = case
            subm_variant['created_at'] = datetime.now()
            ids.append(subm_variant['_id'])

        if self.clinvars_from_clinvarid(submission_id=submission_obj[0]['clinvar_submission']):
            return "clinvar submission id "+submission_obj[0]['clinvar_submission']+" already exists in database!","danger"
        elif self.clinvars_from_variantids(ids):
            return "One of more variants your are trying to save is already present in a clinvar submission!","danger"
        else:
            logger.info("Adding clinvar submission id: {0}".format(submission_obj[0]['clinvar_submission']))
            result = self.clinvar_collection.insert_many(submission_obj)
            return "variants with ids {0} were saved into clinvar submission collection".format(result.inserted_ids), "success"


    def clinvars_from_variantids(self, variant_ids):
        """Fetch a list of clinvar submissions by providing the variant id (list of _id)

            Args:
                variant ids ([_id])

            Returns:
                list of any submission found for these variants
        """
        logger.debug("Fetch clinvar submissions with variant _id {}".format(variant_ids))
        submission_objs = [ subm for subm in self.clinvar_collection.find( { "_id" : { "$in" : variant_ids }} ).sort('clinvar_submission',pymongo.DESCENDING)]

        if len(submission_objs) == 0:
            logger.debug("Could not find clinvar submissions for variants {0}".format(variant_ids))
            return None
        else:
            return submission_objs


    def clinvars_from_case(self, case):
        """Fetch a clinvar submission (all variants submitted) for a given case id

            Args:
                case id(str)

            Returns:
                list of submitted variants with submission id
        """
        logger.debug("Fetch clinvar submission id for case {}".format(case))
        submissions = [ subm for subm in self.clinvar_collection.find({ 'case' : case }).sort('clinvar_submission',pymongo.DESCENDING)]

        if submissions:
            return submissions
        else:
            return None


    def clinvars_from_clinvarid(self, submission_id):
        """Fetch a list of submissions by clinvar submission id from the backend

            Args:
                clinvar_id(str)

            Returns:
                list of submission objects
        """
        logger.debug("Fetch clinvar submissions with clinvar id {}".format(submission_id))
        submission_objs = [ subm for subm in self.clinvar_collection.find( {'clinvar_submission': submission_id} ).sort('clinvar_submission',pymongo.DESCENDING)]

        if len(submission_objs) == 0:
            logger.debug("Could not find clinvar submission id {0}".format(submission_id))
            return None
        else:
            return submission_objs

    def add_clinvar_accession(self, variant_id, clinvar_accession):
        """Introduces the field 'clinvar accession' to a variant submitted to clinvar

            Args:
                variant_ids(str)

            Returns: the number of updated documents

        """
        logger.debug("introducing a clinvar accession for clinvar variant {}".format(variant_id))
        new_doc = self.clinvar_collection.find_one_and_update( {"_id": variant_id}, {"$set": {"clinvar_accession": clinvar_accession}}, return_document=pymongo.ReturnDocument.AFTER )
        return new_doc


    def delete_clinvar_submission(self, submission_id):
        """Delete a series of variants submitted to clinvar matching a submission id

            Args:
                clinvar_id(str)

            Returns: the number of deleted variants

        """
        logger.debug("Delete clinvar variants with clinvar submissoon id {}".format(submission_id))
        result = self.clinvar_collection.delete_many( {'clinvar_submission': submission_id} )
        return result.deleted_count
