from pprint import pprint as pp
import pytest


def test_get_manual_rank(real_variant_database):
    adapter = real_variant_database
    
    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()['_id']
    variant = adapter.variant_collection.find_one()
    
    ## WHEN updating variant information for a variant
    var_id = variant['_id']
    variant['manual_rank'] = 3
    adapter.variant_collection.find_one_and_replace({'_id':var_id}, variant)

    
    evaluated_variants = adapter.evaluated_variants(case_id)
    
    ## THEN assert the variant is returned by the function evaluated variants
    assert len(evaluated_variants) == 1

def test_get_commented(real_variant_database):
    adapter = real_variant_database
    
    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()['_id']
    variant = adapter.variant_collection.find_one()

    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 0
    ## WHEN adding the comment for a variant
    var_id = variant['variant_id']
    
    comment = dict(
        institute='cust000',
        case=case_id,
        link='a link',
        category='variant',
        verb='comment',
        variant_id=var_id,
    )
    
    adapter.event_collection.insert_one(comment)

    evaluated_variants = adapter.evaluated_variants(case_id)
    
    ## THEN assert the variant is returned by the function evaluated variants
    assert len(evaluated_variants) == 1

def test_get_ranked_and_commented(real_variant_database):
    adapter = real_variant_database
    
    ## GIVEN a database with information
    case_id = adapter.case_collection.find_one()['_id']
    variant = adapter.variant_collection.find_one()

    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 0
    ## WHEN adding a comment for a variant and updating manual rank
    var_id = variant['variant_id']
    
    comment = dict(
        institute='cust000',
        case=case_id,
        link='a link',
        category='variant',
        verb='comment',
        variant_id=var_id,
    )
    adapter.event_collection.insert_one(comment)
    
    variant['manual_rank'] = 3
    adapter.variant_collection.find_one_and_replace({'_id':variant['_id']}, variant)

    evaluated_variants = adapter.evaluated_variants(case_id)
    
    ## THEN assert the only variant is returned
    assert len(evaluated_variants) == 1