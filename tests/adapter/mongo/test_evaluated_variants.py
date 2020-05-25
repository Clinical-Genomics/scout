from pprint import pprint as pp
import pytest


def test_get_cancer_tier(real_variant_database):
    adapter = real_variant_database

    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()["_id"]
    variant = adapter.variant_collection.find_one()

    ## WHEN updating variant information for a variant
    var_id = variant["_id"]
    variant["cancer_tier"] = "1A"
    adapter.variant_collection.find_one_and_replace({"_id": var_id}, variant)

    evaluated_variants = adapter.evaluated_variants(case_id)

    ## THEN assert the variant is returned by the function evaluated variants
    assert len(evaluated_variants) == 1


def test_get_manual_rank(real_variant_database):
    adapter = real_variant_database

    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()["_id"]
    variant = adapter.variant_collection.find_one()

    ## WHEN updating variant information for a variant
    var_id = variant["_id"]
    variant["manual_rank"] = 3
    adapter.variant_collection.find_one_and_replace({"_id": var_id}, variant)

    evaluated_variants = adapter.evaluated_variants(case_id)

    ## THEN assert the variant is returned by the function evaluated variants
    assert len(evaluated_variants) == 1


def test_get_commented(real_variant_database):
    adapter = real_variant_database

    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()["_id"]
    variant = adapter.variant_collection.find_one()

    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 0
    ## WHEN adding the comment for a variant
    var_id = variant["variant_id"]

    comment = dict(
        institute="cust000",
        case=case_id,
        link="a link",
        category="variant",
        verb="comment",
        variant_id=var_id,
    )

    adapter.event_collection.insert_one(comment)

    evaluated_variants = adapter.evaluated_variants(case_id)

    ## THEN assert the variant is returned by the function evaluated variants
    assert len(evaluated_variants) == 1


def test_get_ranked_and_commented(real_variant_database):
    adapter = real_variant_database

    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()["_id"]
    variant = adapter.variant_collection.find_one()

    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 0
    ## WHEN adding a comment for a variant and updating manual rank
    var_id = variant["variant_id"]

    comment = dict(
        institute="cust000",
        case=case_id,
        link="a link",
        category="variant",
        verb="comment",
        variant_id=var_id,
    )
    adapter.event_collection.insert_one(comment)

    variant["manual_rank"] = 3
    adapter.variant_collection.find_one_and_replace({"_id": variant["_id"]}, variant)

    evaluated_variants = adapter.evaluated_variants(case_id)

    ## THEN assert the only variant is returned
    assert len(evaluated_variants) == 1


def test_get_ranked_and_comment_two(real_variant_database):
    adapter = real_variant_database

    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()["_id"]
    variants = adapter.variant_collection.find()

    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 0
    ## WHEN adding a comment for a variant and updating manual rank
    for i, variant in enumerate(variants):
        if i > 1:
            break

        var_id = variant["variant_id"]

        comment = dict(
            institute="cust000",
            case=case_id,
            link="a link",
            category="variant",
            verb="comment",
            variant_id=var_id,
        )
        adapter.event_collection.insert_one(comment)

        variant["manual_rank"] = 3
        adapter.variant_collection.find_one_and_replace({"_id": variant["_id"]}, variant)

    evaluated_variants = adapter.evaluated_variants(case_id)

    ## THEN assert the only variant is returned
    assert len(evaluated_variants) == 2


def test_evaluated_variants(
    case_obj, institute_obj, user_obj, real_populated_database, variant_objs
):

    adapter = real_populated_database
    case_id = case_obj["_id"]

    # Assert that the database contains no variant yet
    res = adapter.variants(case_id=case_id, nr_of_variants=-1)
    assert sum(1 for i in res) == 0

    # Add to the empty database all variants from variant_objs
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # Assert that the database contains variants now
    n_documents = sum(1 for i in adapter.variant_collection.find())
    assert n_documents > 0

    ## I want to test for the existence of variants with the following keys:
    ## acmg_classification, manual_rank, dismiss_variant so I need to add these keys with values to variants in the database:

    # Collect four variants from tyhe database
    test_variants = list(adapter.variant_collection.find().limit(4))

    # Add the 'acmg_classification' key with a value to one variant:
    acmg_variant = test_variants[0]
    adapter.variant_collection.find_one_and_update(
        {"_id": acmg_variant["_id"]}, {"$set": {"acmg_classification": 4}}
    )

    # Add the 'manual_rank' key with a value to another variant:
    manual_ranked_variant = test_variants[1]
    adapter.variant_collection.find_one_and_update(
        {"_id": manual_ranked_variant["_id"]}, {"$set": {"manual_rank": 1}}
    )

    # Add the 'dismiss_variant' key with a value to another variant:
    dismissed_variant = test_variants[2]
    adapter.variant_collection.find_one_and_update(
        {"_id": dismissed_variant["_id"]}, {"$set": {"dismiss_variant": 22}}
    )

    # Add a comment event to the events collection for a variant:
    commented_variant = test_variants[3]

    # Insert a comment event for this variant:
    adapter.create_event(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="a link",
        category="variant",
        verb="comment",
        subject="This is a comment for a variant",
        level="specific",
        variant=commented_variant,
    )

    # Check that four variants (one ACMG-classified, one manual-ranked, one dismissed and one with comment) are retrieved from the database:
    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 4
