def test_case_mme_update(adapter, case_obj, user_obj, mme_patient, institute_obj, mme_submission):
    """ Test the function that registers an effected individual as submitted to MatchMaker """
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    mme_submission["server_responses"] = [{"patient": mme_patient}]

    ## GIVEN a database without cases with MME submission:
    adapter.case_collection.find_one({"mme_submission": {"$exists": True}}) is None

    updated_case = adapter.case_mme_update(case_obj, user_obj, mme_submission)

    # One case has MME submission now
    assert updated_case["mme_submission"]
    assert adapter.case_collection.find_one({"mme_submission": {"$exists": True}})


def test_case_mme_delete(adapter, case_obj, user_obj, institute_obj, mme_patient):
    """ Test the function that updates a case by deleting a MME submission associated to it """
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    mme_subm_obj = "mock_submission_object"

    # Register a MME submission for a case
    adapter.case_collection.update_one(
        {"_id": case_obj["_id"]}, {"$set": {"mme_submission": mme_subm_obj}}
    )
    submitted_case = adapter.case_collection.find_one({"mme_submission": {"$exists": True}})

    assert submitted_case["mme_submission"] == mme_subm_obj

    # Now remove submission using the adapter function
    updated_case = adapter.case_mme_delete(submitted_case, user_obj)

    # Case should not have associated MME submission data any more
    assert updated_case["mme_submission"] is None
