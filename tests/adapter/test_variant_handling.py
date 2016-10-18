import logging

def test_load_variants(populated_database, variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    case_id = case_obj.case_id
    # Make sure that there are no variants in the database
    assert populated_database.variants(case_id=case_id, nr_of_variants=-1).count() == 0
    
    for index, variant_obj in enumerate(variant_objs):
        populated_database.load_variant(variant_obj)
    
    # Make sure that there are no variants in the database
    assert populated_database.variants(case_id=case_id, nr_of_variants=-1).count() == index+1
    