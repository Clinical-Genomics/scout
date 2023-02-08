def test_load_case(case_obj, adapter):
    ## GIVEN a database with no cases
    assert adapter.case_collection.find_one() is None

    ## WHEN loading a case
    adapter._add_case(case_obj)

    ## THEN assert that the case have been loaded with correct info
    assert adapter.case_collection.find_one()


def test_load_case_rank_model_version(case_obj, adapter):
    ## GIVEN a database with no cases
    assert adapter.case_collection.find_one() is None

    ## WHEN loading a case
    adapter._add_case(case_obj)

    ## THEN assert that the case have been loaded with rank_model
    loaded_case = adapter.case_collection.find_one({"_id": case_obj["_id"]})

    assert loaded_case["rank_model_version"] == case_obj["rank_model_version"]
    assert loaded_case["sv_rank_model_version"] == case_obj["sv_rank_model_version"]


def test_load_case_limsid(case_obj, adapter):
    """Test loading a case with lims_id"""

    ## GIVEN a database with no cases
    assert adapter.case_collection.find_one() is None

    ## WHEN loading a case
    adapter._add_case(case_obj)

    ## THEN assert that the case have been loaded with lims id
    loaded_case = adapter.case_collection.find_one({"_id": case_obj["_id"]})

    assert loaded_case["lims_id"] == case_obj["lims_id"]
