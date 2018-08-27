"""
tests/adapter/mongo/test_comment_handling.py

We need to break out some tests from the event function.
"""

def test_specific_comment(adapter, institute_obj, case_obj, user_obj, variant_obj):
    content = 'specific comment for a variant'
    # GIVEN a populated database with a variant and no events
    adapter.variant_collection.insert_one(variant_obj)
    
    assert adapter.variant_collection.find().count() == 1
    assert adapter.event_collection.find().count() == 0

    # WHEN commenting a specific comment on a variant
    updated_variant = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='commentlink',
        variant=variant_obj,
        content=content,
        comment_level='specific'
    )
    # THEN assert that the events function returns the correct event.
    comments = adapter.events(institute_obj, case=case_obj, variant_id=variant_obj['variant_id'], 
                           comments=True)

    for comment in comments:
        assert comment['content'] == content

def test_global_comment(adapter, institute_obj, case_obj, user_obj, variant_obj):
    content = 'global comment for a variant'
    # GIVEN a populated database with a variant and no events
    adapter.variant_collection.insert_one(variant_obj)
    
    assert adapter.variant_collection.find().count() == 1
    assert adapter.event_collection.find().count() == 0

    # WHEN commenting a specific comment on a variant
    updated_variant = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='commentlink',
        variant=variant_obj,
        content=content,
        comment_level='global'
    )
    # THEN assert that the events function returns the correct event.
    comments = adapter.events(institute_obj, case=case_obj, variant_id=variant_obj['variant_id'], 
                           comments=True)

    for comment in comments:
        assert comment['content'] == content
