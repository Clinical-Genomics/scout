# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import pymongo
from bson.objectid import ObjectId
from pymongo import ReturnDocument

LOG = logging.getLogger(__name__)


class ClinVarHandler(object):
    """Class to handle clinvar submissions for the mongo adapter"""

    def create_submission(self, institute_id):
        """Create an open clinvar submission for an institute
        Args:
             institute_id(str): an institute ID

        returns:
             submission(obj): an open clinvar submission object
        """

        submission_obj = {
            "status": "open",
            "created_at": datetime.now(),
            "institute_id": institute_id,
        }
        LOG.info("Creating a new clinvar submission institute %s", institute_id)
        result = self.clinvar_submission_collection.insert_one(submission_obj)
        return result.inserted_id

    def delete_submission(self, submission_id):
        """Deletes a Clinvar submission object, along with all associated clinvar objects (variants and casedata)

        Args:
            submission_id(str): the ID of the submission to be deleted

        Returns:
            deleted_objects(int): the number of associated objects removed (variants and/or casedata)
            deleted_submissions(int): 1 if it's deleted, 0 if something went wrong
        """
        LOG.info("Deleting clinvar submission %s", submission_id)
        submission_obj = self.clinvar_submission_collection.find_one(
            {"_id": ObjectId(submission_id)}
        )

        submission_variants = submission_obj.get("variant_data")
        submission_casedata = submission_obj.get("case_data")

        submission_objects = []

        if submission_variants and submission_casedata:
            submission_objects = submission_variants + submission_casedata
        elif submission_variants:
            submission_objects = submission_variants
        elif submission_casedata:
            submission_objects = submission_casedata

        # Delete all variants and casedata objects associated with this submission
        result = self.clinvar_collection.delete_many({"_id": {"$in": submission_objects}})
        deleted_objects = result.deleted_count

        # Delete the submission itself
        result = self.clinvar_submission_collection.delete_one({"_id": ObjectId(submission_id)})
        deleted_submissions = result.deleted_count

        # return deleted_count, deleted_submissions
        return deleted_objects, deleted_submissions

    def get_open_clinvar_submission(self, institute_id):
        """Retrieve the database id of an open clinvar submission for an institute,
        if none is available then create a new submission and return it

        Args:
             institute_id(str): an institute ID

        Returns:
             submission(obj) : an open clinvar submission object
        """

        LOG.info("Retrieving an open clinvar submission for institute %s", institute_id)
        query = dict(institute_id=institute_id, status="open")
        submission = self.clinvar_submission_collection.find_one(query)

        # If there is no open submission for this institute, create one
        if submission is None:
            submission_id = self.create_submission(institute_id)
            submission = self.clinvar_submission_collection.find_one({"_id": submission_id})

        return submission

    def update_clinvar_id(self, clinvar_id, submission_id):
        """saves an official clinvar submission ID in a clinvar submission object

        Args:
            clinvar_id(str): a string with a format: SUB[0-9]. It is obtained from clinvar portal when starting a new submission
            submission_id(str): submission_id(str) : id of the submission to be updated

        Returns:
            updated_submission(obj): a clinvar submission object, updated
        """
        updated_submission = self.clinvar_submission_collection.find_one_and_update(
            {"_id": ObjectId(submission_id)},
            {"$set": {"clinvar_subm_id": clinvar_id, "updated_at": datetime.now()}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_submission

    def get_clinvar_id(self, submission_id):
        """Returns the official Clinvar submission ID for a submission object

        Args:
            submission_id(str): submission_id(str) : id of the submission

        Returns:
            clinvar_subm_id(str): a string with a format: SUB[0-9]. It is obtained from clinvar portal when starting a new submission

        """
        submission_obj = self.clinvar_submission_collection.find_one(
            {"_id": ObjectId(submission_id)}
        )
        clinvar_subm_id = submission_obj.get(
            "clinvar_subm_id"
        )  # This key does not exist if it was not previously provided by user
        return clinvar_subm_id

    def add_to_submission(self, submission_id, submission_objects):
        """Adds submission_objects to clinvar collection and update the coresponding submission object with their id

        Args:
            submission_id(str) : id of the submission to be updated
            submission_objects(tuple): a tuple of 2 elements coresponding to a list of variants and a list of case data objects to add to submission

        Returns:
            updated_submission(obj): an open clinvar submission object, updated
        """

        LOG.info(
            "Adding new variants and case data to clinvar submission '%s'",
            submission_id,
        )

        # Insert variant submission_objects into clinvar collection
        # Loop over the objects
        for var_obj in submission_objects[0]:
            try:
                result = self.clinvar_collection.insert_one(var_obj)
                self.clinvar_submission_collection.update_one(
                    {"_id": submission_id},
                    {"$push": {"variant_data": str(result.inserted_id)}},
                    upsert=True,
                )
            except pymongo.errors.DuplicateKeyError:
                LOG.error("Attepted to insert a clinvar variant which is already in DB!")

        # Insert casedata submission_objects into clinvar collection
        if submission_objects[1]:
            # Loop over the objects
            for case_obj in submission_objects[1]:
                try:
                    result = self.clinvar_collection.insert_one(case_obj)
                    self.clinvar_submission_collection.update_one(
                        {"_id": submission_id},
                        {"$push": {"case_data": str(result.inserted_id)}},
                        upsert=True,
                    )
                except pymongo.errors.DuplicateKeyError:
                    LOG.error(
                        "One or more casedata object is already present in clinvar collection!"
                    )

        updated_submission = self.clinvar_submission_collection.find_one_and_update(
            {"_id": submission_id},
            {"$set": {"updated_at": datetime.now()}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_submission

    def update_clinvar_submission_status(self, institute_id, submission_id, status):
        """Set a clinvar submission ID to 'closed'

        Args:
            submission_id(str): the ID of the clinvar submission to close

        Return
            updated_submission(obj): the submission object with a 'closed' status

        """
        LOG.info('closing clinvar submission "%s"', submission_id)

        if (
            status == "open"
        ):  # just close the submission its status does not affect the other submissions
            # Close all other submissions for this institute and then open the desired one
            self.clinvar_submission_collection.update_many(
                {"institute_id": institute_id},
                {"$set": {"status": "closed", "updated_at": datetime.now()}},
            )
        updated_submission = self.clinvar_submission_collection.find_one_and_update(
            {"_id": ObjectId(submission_id)},
            {"$set": {"status": status, "updated_at": datetime.now()}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_submission

    def sort_clinvar_case_data(self, variant_list, case_data_list):
        """Sort Case Data for a ClinVar submission reflecting the order of the submission's Variant Data.

        Args:
            variant_list(list): The list of variants in a ClinVar submission (list of dictionaries)
            case_data_list(list): The list of Case info, each relative to a variant in a submission (list of dictionaries)

        Returns:
            sorted_case_data(list): case_data dictionaries sorted according to the order of variants
        """

        # Sort case data according to the order of submissions variant data:
        sorted_case_data = []
        # Loop over submission variants
        for variant_info in variant_list:
            # Loop over submission case data
            for cdata_info in case_data_list:
                # Check that case data linking_id and variant linking_id match to sort case data
                if cdata_info["linking_id"] != variant_info["linking_id"]:
                    continue
                sorted_case_data.append(cdata_info)

        return sorted_case_data or case_data_list

    def clinvar_submissions(self, institute_id):
        """Collect all open and closed clinvar submissions for an institute

        Args:
            institute_id(str): an institute ID

        Returns:
            submissions(list): a list of clinvar submission objects
        """
        LOG.info("Retrieving all clinvar submissions for institute '%s'", institute_id)
        # get first all submission objects
        query = dict(institute_id=institute_id)
        results = list(self.clinvar_submission_collection.find(query))

        submissions = []
        # Loop over all ClinVar submissions for an institute
        for result in results:
            submission = {}
            cases = {}
            submission["_id"] = result.get("_id")
            submission["status"] = result.get("status")
            submission["institute_id"] = result.get("institute_id")
            submission["created_at"] = result.get("created_at")
            submission["updated_at"] = result.get("updated_at")

            if "clinvar_subm_id" in result:
                submission["clinvar_subm_id"] = result["clinvar_subm_id"]

            # If submission has variants registered
            if result.get("variant_data"):
                submission["variant_data"] = list(
                    self.clinvar_collection.find({"_id": {"$in": result["variant_data"]}}).sort(
                        "last_evaluated", pymongo.ASCENDING
                    )
                )

                # Loop over variants contained in a single ClinVar submission
                for var_data_id in list(result["variant_data"]):
                    # get case_id from variant id (caseID_variant_ID)
                    case_id = var_data_id.rsplit("_", 1)[0]
                    case_obj = self.case(case_id=case_id)
                    cases[case_id] = case_obj.get("display_name")

            submission["cases"] = cases

            # If submission has case data registered
            if result.get("case_data"):
                unsorted_case_data = list(
                    self.clinvar_collection.find({"_id": {"$in": result["case_data"]}})
                )
                submission["case_data"] = self.sort_clinvar_case_data(
                    submission.get("variant_data", []), unsorted_case_data or []
                )

            submissions.append(submission)

        return submissions

    def clinvar_objs(self, submission_id, key_id):
        """Collects a list of objects from the clinvar collection (variants of case data) as specified by the key_id in the clinvar submission

        Args:
            submission_id(str): the _id key of a clinvar submission
            key_id(str) : either 'variant_data' or 'case_data'. It's a key in a clinvar_submission object.
                          Its value is a list of ids of clinvar objects (either variants of casedata objects)

        Returns:
            clinvar_objects(list) : a list of clinvar objects (either variants of casedata)

        """
        # Get a submission object
        submission = self.clinvar_submission_collection.find_one({"_id": ObjectId(submission_id)})

        # a list of clinvar object ids, they can be of csv_type 'variant' or 'casedata'
        if submission.get(key_id):
            clinvar_obj_ids = list(submission.get(key_id))
            clinvar_objects = self.clinvar_collection.find({"_id": {"$in": clinvar_obj_ids}})
            return list(clinvar_objects)

        return None

    def rename_casedata_samples(self, submission_id, case_id, old_name, new_name):
        """Rename all samples associated to a clinVar submission

        Args:
            submission_id(str): the _id key of a clinvar submission
            case_id(str): id of case
            old_name(str): old name of an individual in case data
            new_name(str): new name of an individual in case data

        Returns:
            renamed_samples(int)
        """
        renamed_samples = 0
        LOG.info(
            f"Renaming clinvar submission {submission_id}, case {case_id} individual {old_name} to {new_name}"
        )

        casedata_objs = self.clinvar_objs(submission_id, "case_data")

        for obj in casedata_objs:
            if obj.get("individual_id") == old_name and obj.get("case_id") == case_id:
                result = self.clinvar_collection.find_one_and_update(
                    {"_id": obj["_id"]},
                    {"$set": {"individual_id": new_name}},
                    return_document=ReturnDocument.AFTER,
                )
                if result:
                    renamed_samples += 1

        return renamed_samples

    def delete_clinvar_object(self, object_id, object_type, submission_id):
        """Remove a variant object from clinvar database and update the relative submission object

        Args:
            object_id(str) : the id of an object to remove from clinvar_collection database collection (a variant of a case)
            object_type(str) : either 'variant_data' or 'case_data'. It's a key in the clinvar_submission object.
            submission_id(str): the _id key of a clinvar submission

        Returns:
            updated_submission(obj): an updated clinvar submission
        """

        LOG.info("Deleting clinvar object %s (%s)", object_id, object_type)

        # If it's a variant object to be removed:
        #   remove reference to it in the submission object 'variant_data' list field
        #   remove the variant object from clinvar collection
        #   remove casedata object from clinvar collection
        #   remove reference to it in the submission object 'caset_data' list field

        # if it's a casedata object to be removed:
        #   remove reference to it in the submission object 'caset_data' list field
        #   remove casedata object from clinvar collection

        result = ""

        if object_type == "variant_data":
            # pull out a variant from submission object
            self.clinvar_submission_collection.find_one_and_update(
                {"_id": ObjectId(submission_id)}, {"$pull": {"variant_data": object_id}}
            )

            variant_object = self.clinvar_collection.find_one({"_id": object_id})
            linking_id = variant_object.get(
                "linking_id"
            )  # it's the original ID of the variant in scout, it's linking clinvar variants and casedata objects together

            # remove any object with that linking_id from clinvar_collection. This removes variant and casedata
            result = self.clinvar_collection.delete_many({"linking_id": linking_id})

        else:  # remove case_data but keep variant in submission
            # delete the object itself from clinvar_collection
            result = self.clinvar_collection.delete_one({"_id": object_id})

        # in any case remove reference to it in the submission object 'caset_data' list field
        self.clinvar_submission_collection.find_one_and_update(
            {"_id": ObjectId(submission_id)}, {"$pull": {"case_data": object_id}}
        )

        updated_submission = self.clinvar_submission_collection.find_one_and_update(
            {"_id": submission_id},
            {"$set": {"updated_at": datetime.now()}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_submission

    def case_to_clinVars(self, case_id):
        """Get all variants included in clinvar submissions for a case

        Args:
            case_id(str): a case _id

        Returns:
            submission_variants(dict): keys are variant ids and values are variant submission objects

        """
        query = dict(case_id=case_id, csv_type="variant")
        clinvar_objs = list(self.clinvar_collection.find(query))
        submitted_vars = {}
        for clinvar in clinvar_objs:
            submitted_vars[clinvar.get("local_id")] = clinvar

        return submitted_vars
