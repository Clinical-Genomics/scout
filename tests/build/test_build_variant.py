from scout.build import build_variant


def test_build_variant(parsed_variant, institute_obj):
    hgnc_genes = {}
    variant_obj = build_variant(parsed_variant, institute_obj, hgnc_genes)
        
    assert variant_obj.chromosome == parsed_variant['chromosome']
    assert variant_obj.category == 'snv'

def test_build_variants(parsed_variants, institute_obj):
    hgnc_genes = {}
    for variant in parsed_variants:
        variant_obj = build_variant(variant, institute_obj, hgnc_genes)

        assert variant_obj.chromosome == variant['chromosome']
        assert variant_obj.category == 'snv'

def test_build_sv_variant(parsed_sv_variant, institute_obj):
    hgnc_genes = {}
    variant_obj = build_variant(parsed_sv_variant, institute_obj, hgnc_genes)
        
    assert variant_obj.chromosome == parsed_sv_variant['chromosome']
    assert variant_obj.category == 'sv'

def test_build_sv_variants(parsed_sv_variants, institute_obj):
    hgnc_genes = {}
    for variant in parsed_sv_variants:
        variant_obj = build_variant(variant, institute_obj, hgnc_genes)

        assert variant_obj.chromosome == variant['chromosome']
        assert variant_obj.category == 'sv'

def test_build_cadd_score(parsed_variants, institute_obj):
    hgnc_genes = {}
    for index,variant in enumerate(parsed_variants):
        if variant.get('cadd_score'):
            variant_obj = build_variant(variant, institute_obj, hgnc_genes)
            
            assert variant_obj.cadd_score == variant['cadd_score']
            
    assert index > 0