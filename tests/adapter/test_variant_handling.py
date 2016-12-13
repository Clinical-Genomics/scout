import logging

def test_load_variants(populated_database, variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    case_id = case_obj.case_id
    # Make sure that there are no variants in the database
    # GIVEN a populated database without any variants
    # assert populated_database.variants(case_id=case_id, nr_of_variants=-1).count() == 0
    
    # WHEN adding a number of variants
    for index, variant_obj in enumerate(variant_objs):
        populated_database.load_variant(variant_obj)
    
    # THEN the same number of variants should have been loaded
    nr_variants = 0
    result, count = populated_database.variants(case_id=case_id, nr_of_variants=-1)
    assert count == index+1

def test_load_sv_variants(populated_database, sv_variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    case_id = case_obj.case_id

    # GIVEN a populated database without any sv variants
    
    # WHEN adding a number of sv variants
    for index, variant_obj in enumerate(sv_variant_objs):
        populated_database.load_variant(variant_obj)
    
    # THEN the same number of SV variants should have been loaded
    result, count = populated_database.variants(case_id=case_id, nr_of_variants=-1, category='sv')
    assert count == index+1


# def test_get_variant(variant_database):
#     pass
    