"""
tests/adapter/mongo/test_comment_handling.py

We need to break out some tests from the event function.
"""

from pprint import pprint as pp


def test_specific_comment(adapter, institute_obj, case_obj, user_obj, variant_obj):
    content = "specific comment for a variant"
    # GIVEN a populated database with a variant and no events
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) == 1
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # WHEN commenting a specific comment on a variant
    updated_variant = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="commentlink",
        variant=variant_obj,
        content=content,
        comment_level="specific",
    )
    # THEN assert that the events function returns the correct event.
    comments = adapter.events(
        institute_obj,
        case=case_obj,
        variant_id=variant_obj["variant_id"],
        comments=True,
    )

    for comment in comments:
        assert comment["content"] == content

    ## THEN assert that when looking for the comments for a variant in a different case it will not be found
    other_case = case_obj
    other_case["_id"] = "case2"

    comments = adapter.events(
        institute_obj,
        case=other_case,
        variant_id=variant_obj["variant_id"],
        comments=True,
    )
    assert sum(1 for i in comments) == 0


def test_global_comment(adapter, institute_obj, case_obj, user_obj, variant_obj):
    content = "global comment for a variant"
    # GIVEN a populated database with two variants from two cases and no events
    adapter.variant_collection.insert_one(variant_obj)

    assert sum(1 for i in adapter.variant_collection.find()) == 1
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # WHEN commenting a global comment on a variant
    updated_variant = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="commentlink",
        variant=variant_obj,
        content=content,
        comment_level="global",
    )
    # THEN assert that the events function returns the correct event.
    comments = adapter.events(
        institute_obj,
        case=case_obj,
        variant_id=variant_obj["variant_id"],
        comments=True,
    )

    for comment in comments:
        assert comment["content"] == content

    ## THEN assert that when looking for the comments for a variant in a different case one comment should be found
    other_case = case_obj
    other_case["_id"] = "case2"

    comments = adapter.events(
        institute_obj,
        case=other_case,
        variant_id=variant_obj["variant_id"],
        comments=True,
    )
    assert sum(1 for i in comments) == 1


def test_global_and_specific_comments_one_case(
    adapter, institute_obj, case_obj, user_obj, variant_obj
):
    ## GIVEN an adapter with a variant and no events
    adapter.variant_collection.insert_one(variant_obj)

    ## WHEN adding a global and a specific comments
    global_content = "global"
    specific_content = "specific"

    global_comment = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="globalcommentlink",
        variant=variant_obj,
        content=global_content,
        comment_level="global",
    )

    specific_comment = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="specificcommentlink",
        variant=variant_obj,
        content=specific_content,
        comment_level="specific",
    )

    ## THEN assert that when fetching comments for a variant two events are returned
    comments = adapter.events(
        institute=institute_obj,
        case=case_obj,
        variant_id=variant_obj["variant_id"],
        comments=True,
    )
    assert sum(1 for i in comments) == 2


def test_global_and_specific_comments_two_cases_same_institute(
    adapter, institute_obj, case_obj, user_obj, variant_obj
):
    ## GIVEN an adapter with a variant and no events
    adapter.variant_collection.insert_one(variant_obj)

    ## WHEN adding a global and a specific comments for the first variant
    global_content = "global"
    specific_content = "specific"

    # Add a global comment
    global_comment = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="globalcommentlink",
        variant=variant_obj,
        content=global_content,
        comment_level="global",
    )

    # Add a specific comment
    specific_comment = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="globalcommentlink",
        variant=variant_obj,
        content=specific_content,
        comment_level="specific",
    )

    other_case = case_obj
    other_case["case_id"] = other_case["_id"] = "case2"
    other_variant = variant_obj
    other_variant["case_id"] = other_case["case_id"]
    other_variant["_id"] = other_variant["document_id"] = "other_id"

    ## THEN assert that when fetching comments for other variant one global comment should be returned
    comments = adapter.events(
        institute=institute_obj,
        case=other_case,
        variant_id=other_variant["variant_id"],
        comments=True,
    )

    assert sum(1 for i in comments) == 1


def test_global_and_specific_comments_two_cases_different_institutes(
    adapter, institute_obj, case_obj, user_obj, variant_obj
):
    ## GIVEN an adapter with a variant and no events
    adapter.variant_collection.insert_one(variant_obj)

    ## WHEN adding a global and a specific comments for the first variant
    global_content = "global"
    specific_content = "specific"

    # Add a global comment
    global_comment = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="globalcommentlink",
        variant=variant_obj,
        content=global_content,
        comment_level="global",
    )

    # Add a specific comment
    specific_comment = adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="globalcommentlink",
        variant=variant_obj,
        content=specific_content,
        comment_level="specific",
    )

    other_case = case_obj
    other_case["case_id"] = other_case["_id"] = "case2"
    other_variant = variant_obj
    other_variant["case_id"] = other_case["case_id"]
    other_variant["_id"] = other_variant["document_id"] = "other_id"
    other_institute = institute_obj
    other_institute["_id"] = "inst2"

    ## THEN assert that when fetching comments for other variant one global comment should be returned

    comments = adapter.events(
        institute=other_institute,
        case=other_case,
        variant_id=other_variant["variant_id"],
        comments=True,
    )

    assert sum(1 for i in comments) == 1
