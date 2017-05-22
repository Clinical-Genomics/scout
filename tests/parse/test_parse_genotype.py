from scout.parse.variant.genotype import (parse_genotypes, parse_genotype)

def test_parse_genotype(variants):
    ## GIVEN a set of variants and information about the individuals
    ind_ids = variants.samples
    ind_positions = {}
    individuals = {}
    for i, ind in enumerate(ind_ids):
        ind_positions[ind] = i
        individuals[ind] = {
            'individual_id': ind,
            'display_name': ind
        }
        
    ## WHEN parsing the variants genotypes
    for variant in variants:
        
        for ind_id in ind_ids:
            pos = ind_positions[ind_id]
            genotype = parse_genotype(
                            variant=variant, 
                            ind=individuals[ind_id],
                            pos=pos
                        )
    ## THEN assert genotypes are parsed correct
            vcf_genotype = variant.genotypes[pos]
            gt_call = "{0}/{1}".format(vcf_genotype[0], vcf_genotype[1])
            
            vcf_read_depth = int(variant.gt_depths[pos])
            vcf_quality = float(variant.gt_quals[pos])
            
            if vcf_read_depth != -1:
                assert genotype['genotype_call'] == gt_call
                assert genotype['read_depth'] == vcf_read_depth
                assert genotype['genotype_quality'] == vcf_quality

def test_parse_genotypes(variants):
    ## GIVEN a set of variants and information about the individuals
    ind_ids = variants.samples
    ind_positions = {}
    individuals = {}
    case = {}
    for i, ind in enumerate(ind_ids):
        ind_positions[ind] = i
        individuals[ind] = {
            'individual_id': ind,
            'display_name': ind
        }
    case['individuals'] = [individuals[ind_id] for ind_id in individuals]
    ## WHEN parsing the variants genotypes
    for variant in variants:
    
    ## THEN assert genotypes are parsed correct
        
        genotypes = parse_genotypes(variant, case, ind_positions)
        assert len(genotypes) == len(variant.genotypes)
    