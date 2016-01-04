import logging
from scout.ext.backend.utils import get_genotype

def test_get_genotype(variants):
    for variant in variants:
        individuals = list(variant['genotypes'].keys())
        for ind_id in individuals:
            mongo_genotype = get_genotype(
                variant=variant, 
                individual_id=ind_id, 
                display_name=ind_id)
            vcf_genotype = variant['genotypes'][ind_id]
            
            assert mongo_genotype.genotype_call == vcf_genotype.genotype
            assert mongo_genotype.read_depth == vcf_genotype.depth_of_coverage
            assert mongo_genotype.allele_depths == [
                                                vcf_genotype.ref_depth,
                                                vcf_genotype.alt_depth
                                            ]
            assert mongo_genotype.genotype_quality == vcf_genotype.genotype_quality
