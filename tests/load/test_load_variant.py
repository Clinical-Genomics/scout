import pytest

from scout.load.variant import (load_variant, load_variants)

from scout.exceptions.database import IntegrityError


# def test_load_variants(populated_database, variant_objs):
#     """Test to load variants into a mongo database"""
#     pass

def test_load_variant(populated_database, variant_obj):
    """Test to load a variant into a mongo database"""
    adapter = populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    variant_id = load_variant(
        adapter=populated_database,
        variant_obj=variant_obj
    )
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find_one({'_id': variant_id})

def test_load_variant_twice(populated_database, variant_obj):
    """Test to load a variant into a mongo database"""
    adapter = populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database twice
    load_variant(
        adapter=adapter,
        variant_obj=variant_obj
    )

    # THEN a IntegrityError should be raised
    with pytest.raises(IntegrityError):
        load_variant(
            adapter=adapter,
            variant_obj=variant_obj
        )

def test_load_variants(populated_database, case_obj, variant_clinical_file):
    """Test to load a variant into a mongo database"""
    adapter = populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    load_variants(
            adapter=adapter,
            variant_file=variant_clinical_file,
            case_obj=case_obj,
            variant_type='clinical',
            category='snv',
            rank_threshold=rank_threshold,
            chrom=None,
            start=None,
            end=None,
    )
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find().count() > 0

    for variant in adapter.variant_collection.find():
        assert variant['rank_score'] >= rank_threshold
        assert variant['category'] == 'snv'

def test_load_sv_variants(populated_database, case_obj, sv_clinical_file):
    """Test to load a variant into a mongo database"""
    adapter = populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    load_variants(
            adapter=populated_database,
            variant_file=sv_clinical_file,
            case_obj=case_obj,
            variant_type='clinical',
            category='sv',
            rank_threshold=rank_threshold,
            chrom=None,
            start=None,
            end=None,
    )
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find().count() > 0

    for variant in adapter.variant_collection.find():
        assert variant['rank_score'] >= rank_threshold
        assert variant['category'] == 'sv'

def test_load_region(populated_database, case_obj, variant_clinical_file):
    """Test to load variants from a region into a mongo database"""
    adapter = populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    chrom = '1'
    start = 7847367
    end = 156126553
    load_variants(
            adapter=adapter,
            variant_file=variant_clinical_file,
            case_obj=case_obj,
            variant_type='clinical',
            category='snv',
            chrom=chrom,
            start=start,
            end=end,
    )
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find().count() > 0

    for variant in adapter.variant_collection.find():
        assert variant['chromosome'] == chrom
        assert variant['position'] <= end
        assert variant['end'] >= start
