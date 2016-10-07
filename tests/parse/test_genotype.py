from scout.parse.genotype import (parse_genotypes, parse_genotype)

def test_parse_genotype(variants):
    for variant in variants:
        ind_ids = list(variant['genotypes'].keys())
        individuals = {}
        for ind_id in ind_ids:
            individuals[ind_id] = {
                'ind_id': ind_id,
                'display_name': ind_id
                
            }
        for ind_id in individuals:
            genotype = parse_genotype(variant=variant, ind=individuals[ind_id])
            
            vcf_genotype = variant['genotypes'][ind_id]
            
            print(vcf_genotype)
            assert genotype['genotype_call'] == vcf_genotype.genotype
            assert genotype['read_depth'] == vcf_genotype.depth_of_coverage
            assert genotype['ref_depth'] == vcf_genotype.ref_depth 
            assert genotype['alt_depth'] == vcf_genotype.alt_depth 
            assert genotype['genotype_quality'] == vcf_genotype.genotype_quality

def test_parse_genotypes(variants):
    
    for variant in variants:
        ind_ids = list(variant['genotypes'].keys())
        individuals = []
        for ind_id in ind_ids:
            individuals.append({
                'ind_id': ind_id,
                'display_name': ind_id
            })
        case = {'individuals': individuals}
        
        genotypes = parse_genotypes(variant, case)
        assert len(genotypes) == len(variant['genotypes'])
    