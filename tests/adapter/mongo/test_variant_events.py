import datetime
import logging
from copy import deepcopy

import pymongo
import pytest

from scout.constants import VERBS_MAP


def test_matching_tiered(adapter, institute_obj, cancer_case_obj, user_obj, cancer_variant_obj):
    """Test retrieving matching tiered variants from other cancer cases"""

    # GIVEN a database containing a cancer variant in another case
    other_var = deepcopy(cancer_variant_obj)
    other_var["_id"] = "another_id"
    other_var["case"] = cancer_case_obj["_id"]
    other_var["cancer_tier"] = "1A"
    other_var["owner"] = institute_obj["_id"]
    adapter.variant_collection.insert_one(other_var)

    cancer_tier = "1A"

    # GIVEN that the other variant is tiared
    adapter.update_cancer_tier(
        institute=institute_obj,
        case=cancer_case_obj,
        user=user_obj,
        link="link",
        variant=other_var,
        cancer_tier=cancer_tier,
    )

    # WHEN retrieving other tiered variants matching the query variant
    matching_tiered = adapter.matching_tiered(
        query_variant=cancer_variant_obj, user_institutes=[{"_id": "cust000"}]
    )

    # THEN it should return a set with the other variant tier info
    assert matching_tiered == {"1A": {"label": "danger", "links": {"link"}}}


def test_mark_causative(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a populated database with variants
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    variant = adapter.variant_collection.find_one()

    link = "markCausativelink"
    ## WHEN marking a variant as causative
    updated_case = adapter.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
    )
    # THEN the case should have a causative variant
    assert len(updated_case["causatives"]) == 1
    # THEN two events should have been created, one for the case and one for the variant
    assert sum(1 for i in adapter.event_collection.find()) == 2

    # THEN assert that case status is updated to solved
    assert updated_case["status"] == "solved"

    event_obj = adapter.event_collection.find_one()
    assert event_obj["link"] == link


def test_unmark_causative(adapter, institute_obj, case_obj, user_obj, variant_obj):

    ## GIVEN a adapter with a variant that is marked causative
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    link = "markCausativelink"
    updated_case = adapter.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
    )

    variant = adapter.variant_collection.find_one()

    ## WHEN unmarking a variant as causative
    unmark_link = "unMarkCausativelink"
    updated_case = adapter.unmark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=unmark_link,
        variant=variant,
    )

    ## THEN assert that the case has no causatives
    assert len(updated_case["causatives"]) == 0
    ## THEN assert that the case is not solved
    assert updated_case["status"] == "active"
    ## THEN assert that two more events was created

    assert sum(1 for i in adapter.event_collection.find()) == 4


def test_mark_partial_causative(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a populated database with variants
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # And at least a phenotype (OMIM diagnosis or HPO terms)
    omim_terms = ["145590", "615349"]
    hpo_terms = ["Febrile seizures_HP:0002373"]

    # When marking the variant as partial causative
    ## WHEN marking a variant as causative
    updated_case = adapter.mark_partial_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="link_to_partial_causative_variant",
        variant=variant_obj,
        omim_terms=omim_terms,
        hpo_terms=hpo_terms,
    )

    # Then the updated case status should'n be marked as solved
    assert updated_case["status"] != "solved"

    # Shoud have one partial causative variant
    assert len(updated_case["partial_causatives"].keys()) == 1

    # And 2 associated events should be created in database
    assert sum(1 for i in adapter.event_collection.find()) == 2


def test_unmark_partial_causative(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a populated database with variants
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # And at least a phenotype (OMIM diagnosis or HPO terms)
    omim_terms = ["145590", "615349"]
    hpo_terms = ["Febrile seizures_HP:0002373"]

    # When marking the variant as partial causative
    ## WHEN marking a variant as causative
    updated_case = adapter.mark_partial_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="link_to_partial_causative_variant",
        variant=variant_obj,
        omim_terms=omim_terms,
        hpo_terms=hpo_terms,
    )

    assert updated_case["partial_causatives"][variant_obj["_id"]]

    ## WHEN unmarking a variant as causative
    unmark_link = "unMarkPartialCausativelink"
    updated_case = adapter.unmark_partial_causative(
        institute=institute_obj,
        case=updated_case,
        user=user_obj,
        link=unmark_link,
        variant=variant_obj,
    )

    ## THEN assert that the case has no causatives
    assert len(updated_case["partial_causatives"]) == 0

    ## THEN assert that two more events was created
    assert sum(1 for i in adapter.event_collection.find()) == 4


def test_order_verification(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a populated database with variants
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    variant = adapter.variant_collection.find_one()
    assert variant.get("sanger_ordered") is not True

    link = "orderSangerlink"
    # WHEN ordering sanger for a variant
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant,
    )

    # THEN one events should have been created, one for the variant
    assert sum(1 for i in adapter.event_collection.find()) == 2

    # THEN updated variant should have same id as original variant
    assert variant.get("_id") == updated_variant.get("_id")

    # THEN the variant should be marked for sanger analysis
    assert updated_variant.get("sanger_ordered") is True

    for event_obj in adapter.event_collection.find():
        assert event_obj["link"] == link
        assert event_obj["verb"] == "sanger"
        assert event_obj["category"] in ["case", "variant"]


def test_cancel_verification(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a populated database with a variant that has sanger ordered
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    link = "orderSangerlink"
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
    )

    variant = adapter.variant_collection.find_one()
    assert variant.get("sanger_ordered") is not False

    # WHEN canceline sanger ordering for a variant
    cancel_link = "cancelSangerlink"
    updated_variant = adapter.cancel_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=cancel_link,
        variant=variant,
    )

    # THEN updated variant should have same id as original variant
    assert variant.get("_id") == updated_variant.get("_id")

    # THEN the variant should be marked for sanger analysis
    assert updated_variant.get("sanger_ordered") is False


def test_dismiss_variant(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a variant db with at least one variant, and no events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    variant = adapter.variant_collection.find_one()

    assert variant.get("dismiss_variant") == None

    # WHEN dismissing a variant

    link = "testDismissMyVariant"

    dismiss_reason = [3, 5, 7]

    updated_variant = adapter.update_dismiss_variant(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant,
        dismiss_variant=dismiss_reason,
    )

    # THEN a dismiss event should be created
    event_obj = adapter.event_collection.find_one()
    assert event_obj["verb"] == "dismiss_variant"

    # THEN the variant should be dismissed
    assert updated_variant.get("dismiss_variant") == dismiss_reason


def test_update_cancer_tier(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a variant db with at least one variant, and no events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    variant = adapter.variant_collection.find_one()

    assert variant.get("cancer_tier") == None

    # WHEN upating cancer tier
    link = "testUpdateCancerTier"

    cancer_tier = "1A"

    updated_variant = adapter.update_cancer_tier(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant,
        cancer_tier=cancer_tier,
    )

    # THEN an event should be created
    event_obj = adapter.event_collection.find_one()
    assert event_obj["verb"] == "cancer_tier"

    # THEN the variant should be given the appropriate tier
    assert updated_variant.get("cancer_tier") == cancer_tier


def test_update_manual_rank(adapter, institute_obj, case_obj, user_obj, variant_obj):

    # GIVEN a variant db with at least one variant, and no events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) > 0
    assert sum(1 for i in adapter.event_collection.find()) == 0

    variant = adapter.variant_collection.find_one()

    assert variant.get("manual_rank") == None

    # WHEN upating cancer tier
    link = "testUpdateManualRank"

    manual_rank = "1"

    updated_variant = adapter.update_manual_rank(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant,
        manual_rank=manual_rank,
    )

    # THEN an event should be created
    event_obj = adapter.event_collection.find_one()
    assert event_obj["verb"] == "manual_rank"

    # THEN the variant should be given the appropriate rank
    assert updated_variant.get("manual_rank") == manual_rank


def test_sanger_ordered(adapter, institute_obj, case_obj, user_obj, variant_obj):
    """Test function that retrieved all variants ordered by institute, user or case"""

    # GIVEN a variant db with at least one variant, and no events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    # WHEN ordering sanger for the variant
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="orderSangerlink",
        variant=variant_obj,
    )
    updated_variant = adapter.variant_collection.find_one()

    # THEN the 'sanger_ordered' function should retrieve the variant
    # by querying database using the user_id
    sanger_results = adapter.sanger_ordered(user_id=user_obj["_id"])
    assert sanger_results[0]["_id"] == case_obj["_id"]
    assert [var for var in sanger_results[0]["vars"]] == [updated_variant["variant_id"]]

    # by querying database using the institute_id
    sanger_results = adapter.sanger_ordered(institute_id=institute_obj["_id"])
    assert sanger_results[0]["_id"] == case_obj["_id"]
    assert [var for var in sanger_results[0]["vars"]] == [updated_variant["variant_id"]]

    # or by querying database using the case id
    sanger_results = adapter.sanger_ordered(case_id=case_obj["_id"])
    assert sanger_results[0]["_id"] == case_obj["_id"]
    assert [var for var in sanger_results[0]["vars"]] == [updated_variant["variant_id"]]
