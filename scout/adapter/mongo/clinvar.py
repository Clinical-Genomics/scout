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

        if self.clinvars_from_clinvarid(clinvar_id=submission_obj[0]['clinvar_submission']):
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
        submission_objs = self.clinvar_collection.find({
            "_id" : { "$in" : variant_ids }
        })

        if submission_objs.count() == 0:
            logger.debug("Could not find clinvar submissions for variants {0}".format(variant_ids))
            return None
        else:
            return submission_objs


    def clinvarid_from_case(self, case):
        """Fetch a clinvar submission id for a given case id

            Args:
                case id(str)

            Returns:
                submission id(str)
        """
        logger.debug("Fetch clinvar submission id for case {}".format(case))
        submission = self.clinvar_collection.find_one({ 'case' : case })

        if submission:
            return submission['clinvar_submission']
        else:
            return None


    def clinvars_from_clinvarid(self, clinvar_id):
        """Fetch a list of submissions by clinvar submission id from the backend

            Args:
                clinvar_id(str)

            Returns:
                list of submission objects
        """
        logger.debug("Fetch clinvar submissions with clinvar id {}".format(clinvar_id))
        submission_objs = self.clinvar_collection.find({
            'clinvar_submission': clinvar_id
        })

        if submission_objs.count() == 0:
            logger.debug("Could not find clinvar submission id {0}".format(clinvar_id))
            return None
        else:
            return submission_objs
