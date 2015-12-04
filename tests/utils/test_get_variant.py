from scout.ext.backend.utils import get_mongo_variant

from vcf_parser import VCFParser

one_variant = "tests/fixtures/337334.one_variant.clinical.vcf"

def test_get_mongo_variant(setup_database, vcf_case, get_institute):
    variant_parser = VCFParser(infile=one_variant)
    variants = []
    individuals = variant_parser.individuals
    scout_individuals = {ind_id:ind_id for ind_id in individuals}
    
    for variant in variant_parser:
        variants.append(variant)
    variant = variants[0]
    mongo_variant = get_mongo_variant(
                        variant=variant,
                        variant_type='clinical',
                        individuals=scout_individuals,
                        case=vcf_case,
                        institute=get_institute,
                        variant_count=100
                    )
    
    assert mongo_variant.chromosome == '14'
    assert mongo_variant.reference == 'C'
    assert mongo_variant.alternative == 'A'


    assert len(mongo_variant.genes) == 2
    assert len(mongo_variant.compounds) == 3
