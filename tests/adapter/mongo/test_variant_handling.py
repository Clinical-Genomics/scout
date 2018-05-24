import os
import logging

import pytest

TRAVIS = os.getenv('TRAVIS')

log = logging.getLogger(__name__)

def test_load_variants(real_populated_database, variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    adapter = real_populated_database
    case_id = case_obj['_id']
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
    assert result.count() == index + 1

# def test_manual_rank(real_populated_database, variant_objs, case_obj):
#     """Check that the manual rank is added"""
#     adapter = real_populated_database
#     case_id = case_obj['_id']
#     # Make sure that there are no variants in the database
#     # GIVEN a populated database without any variants
#     assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0
#
#     # WHEN adding a number of variants
#     for index, variant_obj in enumerate(variant_objs):
#         # print(variant_obj)
#         adapter.load_variant(variant_obj)
#
#     # THEN the same number of variants should have been loaded
#     result = adapter.variants(case_id=case_id, nr_of_variants=-1)
#     log.info("Number of variants loaded:%s", result.count())
#
#     for variant in result:
#         assert 'variant_rank' in variant


def test_load_sv_variants(real_populated_database, sv_variant_objs, case_obj):
    """Test to load variants into a mongo database"""
    adapter = real_populated_database
    case_id = case_obj['_id']

    # GIVEN a populated database without any sv variants
    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    # WHEN adding a number of sv variants
    for index, variant_obj in enumerate(sv_variant_objs):
        adapter.load_variant(variant_obj)

    # THEN the same number of SV variants should have been loaded
    result = adapter.variants(case_id=case_id, nr_of_variants=-1, category='sv')
    assert result.count() == index + 1


def test_load_all_variants(real_populated_database, case_obj):
    adapter = real_populated_database
    case_id = case_obj['_id']

    ## GIVEN a populated database without any variants
    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    ## WHEN loading all variants into the database
    nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                          category='snv', rank_threshold=None, chrom=None,
                          start=None, end=None, gene_obj=None)

    # THEN the same number of SV variants should have been loaded
    result = adapter.variants(case_id=case_id, nr_of_variants=-1, category='snv')

    assert nr_loaded == result.count()

def test_load_whole_gene(real_populated_database, variant_objs, case_obj):
    adapter = real_populated_database
    case_id = case_obj['_id']

    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                          category='snv', rank_threshold=None, chrom=None,
                          start=None, end=None, gene_obj=None)

    ## GIVEN a populated database with variants in a certain gene
    hgnc_id = 3233
    gene_obj = adapter.hgnc_gene(hgnc_id)
    assert gene_obj
    nr_variants_in_gene = adapter.variant_collection.find({'hgnc_ids': hgnc_id}).count()

    ## WHEN loading all variants for that gene
    nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                          category='snv', rank_threshold=None, chrom=None,
                          start=None, end=None, gene_obj=gene_obj)
    new_nr_variants_in_gene = adapter.variant_collection.find({'hgnc_ids': hgnc_id}).count()

    ## Then assert that the other variants where loaded
    assert new_nr_variants_in_gene > nr_variants_in_gene

def test_load_coordinates(real_populated_database, variant_objs, case_obj):
    adapter = real_populated_database
    case_id = case_obj['_id']

    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                          category='snv', rank_threshold=None, chrom=None,
                          start=None, end=None, gene_obj=None)

    ## GIVEN a populated database with variants in a certain gene
    hgnc_id = 3233
    gene_obj = adapter.hgnc_gene(hgnc_id)
    assert gene_obj
    nr_variants_in_gene = adapter.variant_collection.find({'hgnc_ids': hgnc_id}).count()

    ## WHEN loading all variants for that gene
    nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                          category='snv', rank_threshold=None, chrom=gene_obj['chromosome'],
                          start=gene_obj['start'], end=gene_obj['end'], gene_obj=None)

    new_nr_variants_in_gene = adapter.variant_collection.find({'hgnc_ids': hgnc_id}).count()

    ## Then assert that the other variants where loaded
    assert new_nr_variants_in_gene > nr_variants_in_gene

@pytest.mark.skipif(TRAVIS,
                    reason="Tempfiles seems to be problematic on travis")
def test_get_region_vcf(populated_database, case_obj):
    print('Travis', TRAVIS, type(TRAVIS))
    adapter = populated_database
    case_id = case_obj['_id']

    file_name = adapter.get_region_vcf(case_obj, chrom=None, start=None, end=None,
                       gene_obj=None, variant_type='clinical', category='snv',
                       rank_threshold=None)
    ## GIVEN a populated database with variants in a certain gene
    nr_variants = 0
    with open(file_name, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                nr_variants += 1

    os.remove(file_name)

    assert nr_variants > 0


def test_evaluated_variants(case_obj, institute_obj, user_obj, real_populated_database, variant_objs):

    adapter = real_populated_database
    case_id = case_obj['_id']

    # Assert that the database contains no variant yet
    assert adapter.variants(case_id=case_id, nr_of_variants=-1).count() == 0

    # Add to the empty database all variants from variant_objs
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # Assert that the database contains variants now
    n_documents = adapter.variant_collection.find().count()
    assert n_documents > 0

    ## I want to test for the existence of variants with the following keys:
    ## acmg_classification, manual_rank, dismiss_variant so I need to add these keys with values to variants in the database:

    # Collect four variants from tyhe database
    test_variants = list(adapter.variant_collection.find().limit(4))

    # Add the 'acmg_classification' key with a value to one variant:
    acmg_variant = test_variants[0]
    adapter.variant_collection.find_one_and_update({'_id' : acmg_variant['_id']}, {'$set': {'acmg_classification': 4}})

    # Add the 'manual_rank' key with a value to another variant:
    manual_ranked_variant = test_variants[1]
    adapter.variant_collection.find_one_and_update({'_id' : manual_ranked_variant['_id']}, {'$set': {'manual_rank': 1}})

    # Add the 'dismiss_variant' key with a value to another variant:
    dismissed_variant = test_variants[2]
    adapter.variant_collection.find_one_and_update({'_id' : dismissed_variant['_id']}, {'$set': {'dismiss_variant': 22}})

    # Add a comment event to the events collection for a variant:
    commented_variant = test_variants[3]

    # Insert a comment event for this variant:
    adapter.create_event(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='a link',
        category='variant',
        verb='comment',
        subject='This is a comment for a variant',
        level='specific',
        variant = commented_variant
    )

    # Check that four variants (one ACMG-classified, one manual-ranked, one dismissed and one with comment) are retrieved from the database:
    evaluated_variants = adapter.evaluated_variants(case_id)
    assert len(evaluated_variants) == 4
