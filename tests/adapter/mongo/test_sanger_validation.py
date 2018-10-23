# -*- coding: utf-8 -*-
from pprint import pprint as pp
import pytest
from scout.server.blueprints.cases.controllers import get_sanger_unevaluated

def test_get_sanger_unevaluated(real_populated_database, variant_objs, institute_obj, case_obj, user_obj):
    """Test get all sanger ordered but not evaluated for an institute"""

    adapter = real_populated_database

    ## Prepare for variants for Sanger assignment
    # Check that variant collections is empty
    assert adapter.variant_collection.find().count() == 0

    # Adding a number of variants to the empty database
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # Check that variant collections is NOT empty
    assert adapter.variant_collection.find().count() > 0

    # Collect 2 variants from the database
    test_variants = list(adapter.variant_collection.find().limit(2))

    ## Prepare for order Sanger:
    # GIVEN a populated database
    institute = adapter.institute(
        institute_id=institute_obj['internal_id']
    )
    assert institute

    case = adapter.case(
        case_id=case_obj['_id']
    )
    assert case

    user = adapter.user(
        email=user_obj['email']
    )
    assert user

    link = 'orderSangerlink'

    # Order Sanger for both variants
    for variant in test_variants:

        # Assert tha variant has NO Sanger ordered
        assert variant.get('sanger_ordered') == None

        # Assert that variant is not validated
        assert variant.get('validation') == None

        # Order Sanger for variant
        updated_variant = adapter.order_verification(
            institute=institute,
            case=case,
            user=user,
            link=link,
            variant=variant
        )

        # Assert that variant has Sanger ordered now
        assert updated_variant['sanger_ordered']

    # Assert that 4 events were created in events collection (Sanger ordered case X2 + Sanger ordered variant X2)
    assert adapter.event_collection.find().count() == 4

    # Test that the Sanger ordered but not validated for the institute are 2
    # sanger_unevaluated should look like this: [{ 'case_id': [var1, var2] }]
    sanger_unevaluated = get_sanger_unevaluated(adapter, institute['_id'], user_obj['email'])
    assert len(sanger_unevaluated[0][case_obj['display_name']]) == 2

    # Set one of the two variants as validated
    adapter.variant_collection.find_one_and_update(
        {'_id': test_variants[0]['_id']},
        {'$set': {'validation': 'False positive'}},
    )

    # Test that now the Sanger ordered but not validated is only one
    # sanger_unevaluated should look like this: [{ 'case_id': [var2] }]
    sanger_unevaluated = get_sanger_unevaluated(adapter, institute['_id'], user_obj['email'])
    pp(sanger_unevaluated)
    assert len(sanger_unevaluated[0][case_obj['display_name']]) == 1
