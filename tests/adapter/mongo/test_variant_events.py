from pprint import pprint as pp
import pytest
import logging
import datetime
import pymongo

from scout.constants import VERBS_MAP

logger = logging.getLogger(__name__)

def test_mark_causative(adapter, institute_obj, case_obj, user_obj, variant_obj):
    logger.info("Testing mark a variant causative")
    # GIVEN a populated database with variants
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert adapter.variant_collection.find().count() > 0
    assert adapter.event_collection.find().count() == 0

    variant = adapter.variant_collection.find_one()

    link = 'markCausativelink'
    ## WHEN marking a variant as causative
    updated_case = adapter.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj
    )
    # THEN the case should have a causative variant
    assert len(updated_case['causatives']) == 1
    # THEN two events should have been created, one for the case and one for the variant
    assert adapter.event_collection.find().count() == 2

    # THEN assert that case status is updated to solved
    assert updated_case['status'] == 'solved'

    event_obj = adapter.event_collection.find_one()
    assert event_obj['link'] == link

def test_unmark_causative(adapter, institute_obj, case_obj, user_obj, variant_obj):
    logger.info("Testing mark a variant causative")

    ## GIVEN a adapter with a variant that is marked causative
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    link = 'markCausativelink'
    updated_case = adapter.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj
    )

    variant = adapter.variant_collection.find_one()

    ## WHEN unmarking a variant as causative
    unmark_link = 'unMarkCausativelink'
    updated_case = adapter.unmark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=unmark_link,
        variant=variant
    )

    ## THEN assert that the case has no causatives
    assert len(updated_case['causatives']) == 0
    ## THEN assert that the case is not solved
    assert updated_case['status'] == 'active'
    ## THEN assert that two more events was created

    assert adapter.event_collection.find().count() == 4


def test_order_verification(adapter, institute_obj, case_obj, user_obj, variant_obj):
    logger.info("Testing ordering verification for a variant")
    # GIVEN a populated database with variants
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert adapter.variant_collection.find().count() > 0
    assert adapter.event_collection.find().count() == 0

    variant = adapter.variant_collection.find_one()
    assert variant.get('sanger_ordered') is not True

    link = 'orderSangerlink'
    # WHEN ordering sanger for a variant
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant
    )

    # THEN one events should have been created, one for the variant
    assert adapter.event_collection.find().count() == 2

    # THEN updated variant should have same id as original variant
    assert variant.get('_id') == updated_variant.get('_id')

    # THEN the variant should be marked for sanger analysis
    assert updated_variant.get('sanger_ordered') is True

    for event_obj in adapter.event_collection.find():
        assert event_obj['link'] == link
        assert event_obj['verb'] == 'sanger'
        assert event_obj['category'] in ['case', 'variant']


def test_cancel_verification(adapter, institute_obj, case_obj, user_obj, variant_obj):
    logger.info("Testing cancel verification ordering for a variant")
    # GIVEN a populated database with a variant that has sanger ordered
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert adapter.variant_collection.find().count() > 0
    assert adapter.event_collection.find().count() == 0

    link = 'orderSangerlink'
    updated_variant = adapter.order_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj
    )

    variant = adapter.variant_collection.find_one()
    assert variant.get('sanger_ordered') is not False

    # WHEN canceline sanger ordering for a variant
    cancel_link = 'cancelSangerlink'
    updated_variant = adapter.cancel_verification(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=cancel_link,
        variant=variant
    )

    # THEN updated variant should have same id as original variant
    assert variant.get('_id') == updated_variant.get('_id')

    # THEN the variant should be marked for sanger analysis
    assert updated_variant.get('sanger_ordered') is False


def test_dismiss_variant(adapter, institute_obj, case_obj, user_obj, variant_obj):
    logger.info("Test dismiss variant")

    # GIVEN a variant db with at least one variant, and no events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    assert adapter.variant_collection.find().count() > 0
    assert adapter.event_collection.find().count() == 0

    variant = adapter.variant_collection.find_one()

    assert variant.get('dismiss_variant') == None

    # WHEN dismissing a variant

    link = 'testDismissMyVariant'

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
    assert event_obj['verb'] == 'dismiss_variant'

    # THEN the variant should be dismissed
    assert updated_variant.get('dismiss_variant') == dismiss_reason
