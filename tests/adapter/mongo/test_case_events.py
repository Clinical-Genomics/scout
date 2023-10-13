def test_case_dismissed_variants(adapter, institute_obj, case_obj, user_obj, variant_obj):
    """Test adapter function that retrieves the list of dismissed variant ids for a case"""
    # GIVEN a variant db with at least one variant, and no events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.variant_collection.insert_one(variant_obj)

    # WHEN dismissing a variant
    link = "/".join([institute_obj["_id"], case_obj["_id"], variant_obj["_id"]])
    dismiss_reason = [3, 5, 7]
    updated_variant = adapter.update_dismiss_variant(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
        dismiss_variant=dismiss_reason,
    )
    # THEN one event should be found in events collection
    assert sum(1 for i in adapter.event_collection.find()) == 1
    # AND case_dismissed_variants should return a list containing the id of the variant
    assert adapter.case_dismissed_variants(institute_obj, case_obj) == [variant_obj["_id"]]

    # IF the variant dismissed status is reset
    updated_variant = adapter.update_dismiss_variant(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=updated_variant,
        dismiss_variant=[],  # with this list empty the status is reset to not dismissed
    )
    # THEN two events should be found in events collection
    assert sum(1 for i in adapter.event_collection.find()) == 2
    # AND case_dismissed_variants should NOT return a list containing the id of the variant
    assert adapter.case_dismissed_variants(institute_obj, case_obj) == []

    # AND THEN the variant is dismissed again
    updated_variant = adapter.update_dismiss_variant(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=updated_variant,
        dismiss_variant=dismiss_reason,
    )
    # THEN three events should be found in events collection
    assert sum(1 for i in adapter.event_collection.find()) == 3
    # AND case_dismissed_variants should again return a list containing the id of the variant
    assert adapter.case_dismissed_variants(institute_obj, case_obj) == [variant_obj["_id"]]
