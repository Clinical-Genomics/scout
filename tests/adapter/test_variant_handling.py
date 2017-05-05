import logging

log = logging.getLogger(__name__)

def test_load_variants(real_populated_database, variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    adapter = real_populated_database
    case_id = case_obj['case_id']
    # Make sure that there are no variants in the database
    # GIVEN a populated database without any variants
    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0
    
    # WHEN adding a number of variants
    for index, variant_obj in enumerate(variant_objs):
        # print(variant_obj)
        adapter.load_variant(variant_obj)
    
    # THEN the same number of variants should have been loaded
    result = adapter.variants(case_id=case_id, nr_of_variants=-1)
    log.info("Number of variants loaded:%s", result.count())
    assert result.count() == index+1

def test_load_sv_variants(populated_database, sv_variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    case_id = case_obj['case_id']

    # GIVEN a populated database without any sv variants
    assert populated_database.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    # WHEN adding a number of sv variants
    for index, variant_obj in enumerate(sv_variant_objs):
        populated_database.load_variant(variant_obj)

    # THEN the same number of SV variants should have been loaded
    result = populated_database.variants(case_id=case_id, nr_of_variants=-1, category='sv')
    assert result.count() == index+1

def test_load_all_variants(populated_database, variant_objs, case_obj):
    adapter = populated_database
    case_id = case_obj['case_id']
    
    ## GIVEN a populated database without any variants
    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    ## WHEN loading all variants into the database
    nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical', 
                          category='snv', rank_threshold=None, chrom=None, 
                          start=None, end=None, gene_obj=None)

    # THEN the same number of SV variants should have been loaded
    result = populated_database.variants(case_id=case_id, nr_of_variants=-1, category='snv')
    print(adapter.hgnc_gene(3233))
    # assert result.count() == nr_loaded
    # from pprint import pprint as pp
    # for variant in result:
    #     pp(variant)
    # print(nr_loaded)
    assert False
    

# def test_get_variant(variant_database):
#     pass
    