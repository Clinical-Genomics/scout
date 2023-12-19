from cyvcf2 import VCF

from scout.parse.variant.genotype import (
    GENOTYPE_MAP,
    get_alt_depth,
    get_ref_depth,
    parse_genotype,
    parse_genotypes,
)

one_cnvnator = "tests/parse/vcfs/one_cnvnator.vcf"


def test_parse_genotype(variants):
    ## GIVEN a set of variants and information about the individuals
    ind_ids = variants.samples
    ind_positions = {}
    individuals = {}
    for i, ind in enumerate(ind_ids):
        ind_positions[ind] = i
        individuals[ind] = {"individual_id": ind, "display_name": ind}

    ## WHEN parsing the variants genotypes
    for variant in variants:
        for ind_id in ind_ids:
            pos = ind_positions[ind_id]
            genotype = parse_genotype(variant=variant, ind=individuals[ind_id], pos=pos)
            ## THEN assert genotypes are parsed correct
            vcf_genotype = variant.genotypes[pos]
            gt_call = "{0}/{1}".format(GENOTYPE_MAP[vcf_genotype[0]], GENOTYPE_MAP[vcf_genotype[1]])

            vcf_read_depth = int(variant.gt_depths[pos])
            vcf_quality = float(variant.gt_quals[pos])

            if vcf_read_depth != -1:
                assert genotype["genotype_call"] == gt_call
                assert genotype["read_depth"] == vcf_read_depth
                assert genotype["genotype_quality"] == vcf_quality


def test_parse_genotypes(variants):
    ## GIVEN a set of variants and information about the individuals
    ind_ids = variants.samples
    ind_positions = {}
    individuals = {}
    case = {}
    for i, ind in enumerate(ind_ids):
        ind_positions[ind] = i
        individuals[ind] = {"individual_id": ind, "display_name": ind}
    case["individuals"] = [individuals[ind_id] for ind_id in individuals]
    ## WHEN parsing the variants genotypes
    for variant in variants:
        ## THEN assert genotypes are parsed correct

        genotypes = parse_genotypes(variant, case["individuals"], ind_positions)
        assert len(genotypes) == len(variant.genotypes)


def test_parse_cnvnator():
    """docstring for test_parse_cnvnator"""
    vcf_obj = VCF(one_cnvnator)
    for variant in vcf_obj:
        assert variant


def test_get_ref_depth_zeroes(one_variant: "Cyvcf2Variant"):
    """Make sure get_ref_depth returns 0 when provided parameters are all 0."""

    # GIVEN a sample at a given position in the VCF
    position = 2
    # GIVEN a variant which has ref_depth == 0 for that individual
    assert one_variant.gt_ref_depths[position] == 0

    # WHEN ref depth is computed using get_alt_depth function with null parameters
    ref_depth: int = get_ref_depth(
        variant=one_variant,
        pos=position,
        paired_end_ref=0,
        split_read_ref=0,
        spanning_ref=0,
        flanking_ref=0,
        inrepeat_ref=0,
        spanning_mei_ref=0,
    )
    # THEN it should return 0
    assert ref_depth == 0


def test_get_alt_depth_zeroes(one_cyvcf2_fusion_variant: "Cyvcf2Variant"):
    """Make sure get_alt_depth returns 0 when provided parameters are all 0."""

    # GIVEN a sample at a given position in the VCF
    position = 0
    # GIVEN a variant which has alt_depth == -1 for that individual
    assert one_cyvcf2_fusion_variant.gt_alt_depths[position] == -1

    # WHEN alt depth is computed using get_alt_depth function with null parameters
    alt_depth: int = get_alt_depth(
        variant=one_cyvcf2_fusion_variant,
        pos=position,
        paired_end_alt=0,
        split_read_alt=0,
        spanning_alt=0,
        flanking_alt=0,
        inrepeat_alt=0,
        clip5_alt=0,
        clip3_alt=0,
    )
    # THEN it should return 0
    assert alt_depth == 0
