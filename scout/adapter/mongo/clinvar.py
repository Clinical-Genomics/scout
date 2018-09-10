# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from bson.objectid import ObjectId
from scout.exceptions import IntegrityError

import pymongo

LOG = logging.getLogger(__name__)

class ClinVarHandler(object):
    """Class to handle clinvar submissions for the mongo adapter"""

    def create_submission(self, user_id, institute_id):
        """Create an open clinvar submission for a user and an institute
           Args:
                user_id(str): a user ID
                institute_id(str): an institute ID

           returns:
                submission(obj): an open clinvar submission object
        """

        submission_obj = {
            'status' : 'open',
            'created_at' : datetime.now(),
            'user_id' : user_id,
            'institute_id' : institute_id
        }
        LOG.info("Creating a new clinvar submission for user '%s' and institute %s", user_id, institute_id)
        result = self.clinvar_submission_collection.insert_one(submission_obj)
        return result.inserted_id


    def delete_submission(self, submission_id):
        """Deletes a Clinvar submission object, along with all associated clinvar objects (variants and casedata)

            Args:
                submission_id(str): the ID of the submission to be deleted

            Returns:
                result(bool): True or False (If the submission was deleted or not)
        """
        LOG.info("Deleting clinvar submission %s", submission_id)
        submission_obj = self.clinvar_submission_collection.find_one({ '_id' : ObjectId(submission_id)})

        submission_variants = submission_obj['variant_data']
        submission_casedata = submission_obj['case_data']

        # Delete all variants and casedata objects associated with this submission
        result = self.clinvar_collection.delete_many({'_id': { "$in": submission_variants + submission_casedata } })
        deleted_objects = result.deleted_count

        # Delete the submission itself
        result = self.clinvar_submission_collection.delete_one({'_id':ObjectId(submission_id)})
        deleted_submissions = result.deleted_count

        #return deleted_count, deleted_submissions
        return deleted_objects,deleted_submissions



    def get_open_clinvar_submission(self, user_id, institute_id):
        """Retrieve the database id of an open clinvar submission for a user and institute,
           if none is available then create a new submission and return it

           Args:
                user_id(str): a user ID
                institute_id(str): an institute ID

           Returns:
                submission(obj) : an open clinvar submission object
        """

        LOG.info("Retrieving an open clinvar submission for user '%s' and institute %s", user_id, institute_id)
        query = dict(user_id=user_id, institute_id=institute_id, status='open')
        submission = self.clinvar_submission_collection.find_one(query)

        # If there is no open submission for this user and institute, create one
        if submission is None:
            submission_id = self.create_submission(user_id, institute_id)
            submission = self.clinvar_submission_collection.find_one({'_id':submission_id})

        return submission


    def update_submission(self, submission_id, submission_objects):
        """Adds submission_objects to clinvar collection and update the coresponding submission object with their id

            Args:
                submission_id(str) : id of the submission to be updated
                submission_objects(tuple): a tuple of 2 elements coresponding to a list of variants and a list of case data objects to add to submission

            Returns:
                updated_submission(obj): an open clinvar submission object, updated
        """

        LOG.info("Adding new variants and case data to clinvar submission '%s'", submission_id)
        duplicated_variants = []

        # Insert variant submission_objects into clinvar collection
        # Loop over the objects
        for var_obj in submission_objects[0]:
            try:
                result = self.clinvar_collection.insert_one(var_obj)
                self.clinvar_submission_collection.update_one({'_id':submission_id}, {'$push': { 'variant_data' : result.inserted_id }}, upsert=True)
            except pymongo.errors.DuplicateKeyError:
                duplicated_variants.append(var_obj['local_id'])
                LOG.error("Attepted to insert a clinvar variant which is already in DB!")

        # Insert casedata submission_objects into clinvar collection
        if submission_objects[1]:
            # Loop over the objects
            for case_obj in submission_objects[1]:
                try:
                    result = self.clinvar_collection.insert_one(case_obj)
                    self.clinvar_submission_collection.update_one({'_id':submission_id}, {'$push': { 'case_data': result.inserted_id}}, upsert=True)
                except pymongo.errors.DuplicateKeyError:
                    LOG.error("One or more casedata object is already present in clinvar collection!")

        updated_submission = self.clinvar_submission_collection.find_one_and_update( {'_id':submission_id}, { '$set' : {'updated_at': datetime.now()} }, return_document=pymongo.ReturnDocument.AFTER )
        return duplicated_variants


    def update_clinvar_submission_status(self, submission_id, status):
        """Set a clinvar submission ID to 'closed'

            Args:
                submission_id(str): the ID of the clinvar submission to close

            Return
                updated_submission(obj): the submission object with a 'closed' status

        """
        LOG.info('closing clinvar submission "%s"', submission_id)

        updated_submission = self.clinvar_submission_collection.find_one_and_update(
            {'_id'  : ObjectId(submission_id)},
            {'$set' :
                {'status' : status, 'updated_at' : datetime.now()}
            }
        )
        return updated_submission


    def clinvar_submissions(self, user_id, institute_id):
        """Collect all open and closed clinvar submission created by a user for an institute

            Args:
                user_id(str): a user ID
                institute_id(str): an institute ID

            Returns:
                submissions(list): a list of clinvar submission objects
        """

        # get first all submission objects
        query = dict(user_id=user_id, institute_id=institute_id)
        results = list(self.clinvar_submission_collection.find(query))

        submissions = []
        for result in results:
            submission = {}
            submission['_id'] =  result['_id']
            submission['status'] = result['status']
            submission['user_id'] = result['user_id']
            submission['institute_id'] = result['institute_id']
            submission['created_at'] = result['created_at']
            submission['updated_at'] = result['updated_at']

            submission['variant_data'] = list(self.clinvar_collection.find({'_id': { "$in": result['variant_data'] } }))
            if result.get('case_data'):
                submission['case_data'] = list(self.clinvar_collection.find({'_id' : { "$in": result['case_data'] } }))

            submissions.append(submission)

        return submissions


    def clinvar_objs(self, submission_id, key_id):
        """Collects a list of objects from the clinvar collection (variants of case data) as specified by the key_id in the clinvar submission

            Args:
                submission_id(str): The _id key of a clinvar submission
                key_id(str) : either 'variant_data' or 'case_data'. It's a key in a clinvar_submission object.
                              Its value is a list of ids of clinvar objects (either variants of casedata objects)

                clinvar_objects(list) : a list of clinvar objects (either variants of casedata)

        """
        # Get a submission object
        submission = self.clinvar_submission_collection.find_one({"_id": ObjectId(submission_id)})

        # a list of clinvar object ids, they can be of csv_type 'variant' or 'casedata'
        clinvar_obj_ids = list(submission.get(key_id))

        # get a list of objects from a list of their ids
        clinvar_objects = self.clinvar_collection.find({'_id' : { "$in": clinvar_obj_ids }})
        return list(clinvar_objects)
