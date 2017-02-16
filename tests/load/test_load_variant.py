import pytest

from scout.load.variant import (load_variant, load_variants)
from scout.models.variant.variant import Variant

from scout.exceptions.database import IntegrityError


# def test_load_variants(populated_database, variant_objs):
#     """Test to load variants into a mongo database"""
#     pass

def test_load_variant(populated_database, variant_obj):
    """Test to load a variant into a mongo database"""
    # GIVEN a database without any variants
    assert Variant.objects().count() == 0

    # WHEN loading a variant into the database
    load_variant(
        adapter=populated_database,
        variant_obj=variant_obj
    )
    # THEN assert the variant is loaded

    assert Variant.objects.get(variant_id = variant_obj.variant_id)

def test_load_variant_twice(populated_database, variant_obj):
    """Test to load a variant into a mongo database"""
    # GIVEN a database without any variants
    assert Variant.objects().count() == 0

    # WHEN loading a variant into the database twice
    load_variant(
        adapter=populated_database,
        variant_obj=variant_obj
    )

    # THEN a IntegrityError should be raised
    with pytest.raises(IntegrityError):
        load_variant(
            adapter=populated_database,
            variant_obj=variant_obj
        )

def test_load_variants(populated_database, case_obj, variant_clinical_file):
    """Test to load a variant into a mongo database"""
    # GIVEN a database without any variants
    assert Variant.objects().count() == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    load_variants(
            adapter=populated_database,
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

    assert Variant.objects().count() > 0

    for variant in Variant.objects():
        assert variant.rank_score >= rank_threshold
        assert variant.category == 'snv'

def test_load_sv_variants(populated_database, case_obj, sv_clinical_file):
    """Test to load a variant into a mongo database"""
    # GIVEN a database without any variants
    assert Variant.objects().count() == 0

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

    assert Variant.objects().count() > 0

    for variant in Variant.objects():
        assert variant.rank_score >= rank_threshold
        assert variant.category == 'sv'

def test_load_region(populated_database, case_obj, variant_clinical_file):
    """Test to load a variant into a mongo database"""
    # GIVEN a database without any variants
    assert Variant.objects().count() == 0

    # WHEN loading a variant into the database
    chrom = '1'
    start = 7847367
    end = 156126553
    load_variants(
            adapter=populated_database,
            variant_file=variant_clinical_file,
            case_obj=case_obj,
            variant_type='clinical',
            category='snv',
            chrom=chrom,
            start=start,
            end=end,
    )
    # THEN assert the variant is loaded

    assert Variant.objects().count() > 0

    for variant in Variant.objects():
        assert variant.chromosome == chrom
        assert variant.position <= end
        assert variant.end >= start

def test_load_variant_multiple_genes(populated_database, parsed_variant):
    hgnc_ids = []
    hgncid_to_gene = populated_database.hgncid_to_gene()
    
    for i, hgnc_id in enumerate(hgncid_to_gene):
        if i < 100:
            hgnc_ids.append(hgnc_id)

    parsed_variant['hgnc_ids'] = hgnc_ids
    
    from scout.build import build_variant

    institute_id = 'cust000'
    institute_obj = populated_database.institute(institute_id=institute_id)
    variant_obj = build_variant(parsed_variant, institute_obj, hgncid_to_gene = hgncid_to_gene)
    
    assert len(variant_obj['hgnc_ids']) == 100
    
    load_variant(
        adapter=populated_database,
        variant_obj=variant_obj
    )
    
    fetched_variant = Variant.objects.get(variant_id = variant_obj.variant_id)
    
    assert len(fetched_variant['hgnc_ids']) == 100
    assert len(fetched_variant['hgnc_symbols']) == 100

