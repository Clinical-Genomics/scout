# -*- coding: utf-8 -*-
import pymongo
from pprint import pprint as pp
import pytest
from scout.server.blueprints.institutes.controllers import get_sanger_unevaluated


def test_case_sanger_variants(adapter, institute_obj, case_obj, user_obj, variant_obj):
    """Test assigning a verification status to a veriant"""

    ## GIVEN a variant db with at least one variant
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    ## WHEN ordering sanger for a variant
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="orderSangerlink",
        variant=variant_obj,
    )

    case_sanger_vars = adapter.case_sanger_variants(case_id=case_obj["_id"])
    # THEN assert that no verified variants are returned
    assert case_sanger_vars["sanger_verified"] == []
    # THEN assert that one variant with sanger ordered is returned
    assert case_sanger_vars["sanger_ordered"][0]["_id"] == updated_variant["_id"]


def test_case_verified_variants(adapter, institute_obj, case_obj, user_obj, variant_obj):
    """Test assigning a verification status to a veriant"""

    ## GIVEN a variant db with at least one variant
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    ## WHEN setting variant status as verified
    adapter.validate(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="validateSangerlink",
        variant=variant_obj,
        validate_type="True positive",
    )

    case_sanger_vars = adapter.case_sanger_variants(case_id=case_obj["_id"])
    ## THEN assert that one verified variant is found
    assert case_sanger_vars["sanger_verified"][0]["_id"] == variant_obj["_id"]
    ## THEN assert that no variants with sanger ordered exists
    assert case_sanger_vars["sanger_ordered"] == []


def test_case_sanger_and_verified_variants(adapter, institute_obj, case_obj, user_obj, variant_obj):
    """Test assigning a verification status to a veriant"""

    ## GIVEN a variant db with at least one variant
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    ## WHEN ordering sanger for a variant
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="orderSangerlink",
        variant=variant_obj,
    )

    ## WHEN Setting variant status as verified

    adapter.validate(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="validateSangerlink",
        variant=variant_obj,
        validate_type="True positive",
    )

    # Then collecting variants using case_sanger_variants should return the same variant
    case_sanger_vars = adapter.case_sanger_variants(case_id=case_obj["_id"])
    assert case_sanger_vars["sanger_verified"][0]["_id"] == variant_obj["_id"]
    assert case_sanger_vars["sanger_ordered"][0]["_id"] == updated_variant["_id"]


def test_get_sanger_unevaluated(
    real_populated_database, variant_objs, institute_obj, case_obj, user_obj
):
    """Test get all sanger ordered but not evaluated for an institute"""

    adapter = real_populated_database

    ## Prepare for variants for Sanger assignment
    # Check that variant collections is empty
    assert sum(1 for i in adapter.variant_collection.find()) == 0

    # Adding a number of variants to the empty database
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # Check that variant collections is NOT empty
    assert sum(1 for i in adapter.variant_collection.find()) > 0

    # Collect 2 variants from the database
    test_variants = list(adapter.variant_collection.find().limit(2))

    ## Prepare for order Sanger:
    # GIVEN a populated database
    institute = adapter.institute(institute_id=institute_obj["internal_id"])
    assert institute

    case = adapter.case(case_id=case_obj["_id"])
    assert case

    user = adapter.user(email=user_obj["email"])
    assert user

    link = "orderSangerlink"

    # Order Sanger for both variants
    for variant in test_variants:

        # Assert tha variant has NO Sanger ordered
        assert variant.get("sanger_ordered") is None

        # Assert that variant is not validated
        assert variant.get("validation") is None

        # Order Sanger for variant
        updated_variant = adapter.order_verification(
            institute=institute, case=case, user=user, link=link, variant=variant
        )

        # Assert that variant has Sanger ordered now
        assert updated_variant["sanger_ordered"]

    # Assert that 4 events were created in events collection (Sanger ordered case X2 + Sanger ordered variant X2)
    assert sum(1 for i in adapter.event_collection.find()) == 4

    # Test that the Sanger ordered but not validated for the institute are 2
    # sanger_unevaluated should look like this: [{ 'case_id': [var1, var2] }]
    sanger_unevaluated = get_sanger_unevaluated(adapter, institute["_id"], user_obj["email"])
    assert len(sanger_unevaluated[0][case_obj["display_name"]]) == 2

    # Set one of the two variants as validated
    adapter.variant_collection.find_one_and_update(
        {"_id": test_variants[0]["_id"]}, {"$set": {"validation": "False positive"}}
    )

    # Test that now the Sanger ordered but not validated is only one
    # sanger_unevaluated should look like this: [{ 'case_id': [var2] }]
    sanger_unevaluated = get_sanger_unevaluated(adapter, institute["_id"], user_obj["email"])
    pp(sanger_unevaluated)
    assert len(sanger_unevaluated[0][case_obj["display_name"]]) == 1
