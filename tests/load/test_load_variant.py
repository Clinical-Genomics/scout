import pytest
from pprint import pprint as pp

from scout.exceptions.database import IntegrityError
from scout.server.blueprints.variants.controllers import variants

from cyvcf2 import VCF

def test_load_variant(real_populated_database, variant_obj):
    """Test to load a variant into a real mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    adapter.load_variant(variant_obj=variant_obj)
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find_one()

def test_load_variant_twice(real_populated_database, variant_obj):
    """Test to load a variant into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database twice
    adapter.load_variant(variant_obj=variant_obj)

    # THEN a IntegrityError should be raised
    with pytest.raises(IntegrityError):
        adapter.load_variant(variant_obj=variant_obj)

def test_load_variants(real_populated_database, case_obj, variant_clinical_file):
    """Test to load a variant into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    adapter.load_variants(
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
        if variant['chromosome'] != 'MT':
            assert variant['rank_score'] >= rank_threshold
        assert variant['category'] == 'snv'
        assert variant['variant_rank']

def test_load_sv_variants(real_populated_database, case_obj, sv_clinical_file):
    """Test to load a variant into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    rank_threshold = 0
    adapter.load_variants(
            case_obj=case_obj,
            variant_type='clinical',
            category='sv',
            rank_threshold=rank_threshold,
    )
    # THEN assert the variant is loaded

    assert adapter.variant_collection.find().count() > 0

    for variant in adapter.variant_collection.find():
        assert variant['rank_score'] >= rank_threshold
        assert variant['category'] == 'sv'
        assert variant['variant_rank']

def test_load_region(real_populated_database, case_obj, variant_clinical_file):
    """Test to load variants from a region into a mongo database"""
    adapter = real_populated_database
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database
    chrom = '1'
    start = 7847367
    end = 156126553
    adapter.load_variants(
            case_obj=case_obj,
            variant_type='clinical',
            category='snv',
            chrom=chrom,
            start=start,
            end=end,
    )
    # THEN assert all variants loaded are in the given region

    assert adapter.variant_collection.find().count() > 0

    for variant in adapter.variant_collection.find():
        assert variant['chromosome'] == chrom
        assert variant['position'] <= end
        assert variant['end'] >= start

def test_load_mitochondrie(real_populated_database, case_obj, variant_clinical_file):
    """Test that all variants from mt are loaded"""
    adapter = real_populated_database
    rank_threshold = 3
    
    # Check how many MT variants there are in file
    vcf_obj = VCF(variant_clinical_file)
    mt_variants = 0
    for variant in vcf_obj:
        if variant.CHROM == 'MT':
            mt_variants += 1
    
    # Make sure there are some MT variants
    assert mt_variants
    
    # GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0

    # WHEN loading a variant into the database

    adapter.load_variants(
            case_obj=case_obj,
            variant_type='clinical',
            category='snv',
            rank_threshold = rank_threshold,
    )
    # THEN assert all MT variants is loaded

    mt_variants_found = 0
    for variant in adapter.variant_collection.find():
        if variant['chromosome'] == 'MT':
            mt_variants_found += 1
        else:
            assert variant['rank_score'] >= rank_threshold

    assert mt_variants == mt_variants_found

def test_compounds_region(real_populated_database, case_obj):
    """When loading the variants not all variants will be loaded, only the ones that
       have a rank score above a treshold.
       This implies that some compounds will have the status 'not_loaded'=True.
       When loading all variants for a region then all variants should 
       have status 'not_loaded'=False.
    """
    adapter = real_populated_database
    variant_type = 'clinical'
    category = 'snv'
    ## GIVEN a database without any variants
    assert adapter.variant_collection.find().count() == 0
    
    ## WHEN loading a variant into the database
    adapter.load_variants(
            case_obj=case_obj,
            variant_type=variant_type,
            category=category,
            rank_threshold=-10
    )
    
    adapter.load_indexes()
    institute_obj = adapter.institute_collection.find_one()
    case_obj = adapter.case_collection.find_one()
    
    chrom = '1'
    start = 156112157
    end = 156152543
    
    query = adapter.build_query(
                case_id=case_obj['_id'],
                query={
                    'variant_type': variant_type,
                    'chrom': chrom,
                    'start': start,
                    'end': end,
                },
                category=category
            )
    ## THEN assert that there are variants with compounds without information
    variants_query = adapter.variant_collection.find(query)
    nr_comps = 0
    nr_variants = 0
    nr_not_loaded = 0
    genomic_regions = adapter.get_coding_intervals()
    for nr_variants,variant in enumerate(variants_query):
        for comp in variant.get('compounds',[]):
            nr_comps += 1
            if comp['not_loaded']:
                nr_not_loaded += 1
    
    assert nr_not_loaded > 0
    assert nr_variants > 0
    assert nr_comps > 0

    ## THEN when loading all variants in the region, assert that ALL the compounds are updated
    print('')
    adapter.load_variants(
            case_obj=case_obj,
            variant_type=variant_type,
            category=category,
            chrom=chrom,
            start=start,
            end=end
            )

    variants_query = adapter.variant_collection.find(query)
    nr_comps = 0
    nr_variants = 0
    for nr_variants,variant in enumerate(variants_query):
        for comp in variant.get('compounds',[]):
            nr_comps += 1
            # We know that all ar updated and loaded if this flag is set
            assert comp['not_loaded'] == False
    
    assert nr_variants > 0
    assert nr_comps > 0

def test_updated_panel(real_variant_database, case_obj):
    """Test if the annotated panels are correct on variant level when a gene is removed 
    from the panel. Ref #754
    
    In this test we need to update a gene panel by removing some genes and check that when loading
      variants they should not be annotated with the panel.
    
    """
    adapter = real_variant_database
    
    ## GIVEN an adapter with variants case and everything
    
    # Collect the hgnc_ids for all genes in the panel
    panel_hgnc_ids = set()
    # Get the panel object
    panel_name = case_obj['panels'][0]['panel_name']
    panel_obj = adapter.gene_panel(panel_name)
    for gene_obj in panel_obj['genes']:
        # Add the existing hgnc ids to the panel
        panel_hgnc_ids.add(gene_obj['hgnc_id'])
    
    # Loop over the variants and check that there are variants in
    # the genes from the panel
    variants = adapter.variants(case_id=case_obj['_id'])
    
    # Collect all present hgnc ids from the variants
    variant_hgnc_ids = set() 
    for variant in variants:
        # print(variant['hgnc_ids'])
        if variant.get('hgnc_ids'):
            for hgnc_id in variant['hgnc_ids']:
                if hgnc_id in panel_hgnc_ids:
                    # assert that the panel is annotated on the variant
                    assert panel_name in variant['panels']
                variant_hgnc_ids.add(hgnc_id)
    
    # Assert that there are data
    assert panel_hgnc_ids
    assert variant_hgnc_ids
    
    intersecting_ids = panel_hgnc_ids.intersection(variant_hgnc_ids)
    assert intersecting_ids
    
    # Create a new case and a new gene panel
    
    # Create and insert a new gene panel without the intersecting genes
    old_panel_genes = panel_obj['genes']
    panel_obj['genes'] = []
    for gene in old_panel_genes:
        if gene['hgnc_id'] not in intersecting_ids:
            panel_obj['genes'].append(gene)
    
    new_version = panel_obj['version'] + 1
    panel_obj['version'] = new_version
    panel_obj.pop('_id')
    
    adapter.panel_collection.insert_one(panel_obj)
    
    new_panel = adapter.panel_collection.find_one({'panel_name': panel_obj['panel_name'], 'version': new_version})
    new_panel_ids = set()
    
    for gene in new_panel['genes']:
        hgnc_id = gene['hgnc_id']
        new_panel_ids.add(hgnc_id)
        assert hgnc_id not in intersecting_ids
    
    # Create a new case with the new panel
    case_obj['_id'] = 'second_case'
    case_obj['panels'][0]['version'] = new_panel['version']
    case_obj['panels'][0]['panel_id'] =  new_panel['_id']

    # Insert the new case and the variants
    adapter._add_case(case_obj)
    
    new_caseobj = adapter.case_collection.find_one({'_id': 'second_case'})
    
    adapter.load_variants(
        new_caseobj, 
        variant_type='clinical', 
        category='snv',
        rank_threshold=-10,
        build='37'
    )
    
    # These are the new variants
    new_variants = adapter.variant_collection.find({'case_id': case_obj['_id']})
    
    nr_variants = 0
    for variant in new_variants:
        if variant.get('hgnc_ids'):
            for hgnc_id in variant['hgnc_ids']:
                if hgnc_id in intersecting_ids:
                    # assert that the panel is NOT annotated on the variant
                    # We removed the gener from the new panel
                    assert panel_name not in variant.get('panels',[])
                    nr_variants += 1
    assert nr_variants > 0
