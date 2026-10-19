import pytest
from cyvcf2 import VCF

from scout.parse.variant.genotype import (
    GENOTYPE_MAP,
    _extract_genotype_alleles,
    _parse_format_entry_trgt_mc,
    get_alt_depth,
    get_copy_number,
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
        sd_ref=0,
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
        sd_alt=0,
        clip5_alt=0,
        clip3_alt=0,
    )
    # THEN it should return 0
    assert alt_depth == 0


def test_parse_pathologic_struc(one_trgt_variant, one_individual):
    """Test parsing PathologicStruc from TRGT style STRs"""

    # GIVEN an STR variant, with a PathologicStruc entry and a corresponding mc set
    assert one_trgt_variant.INFO.get("PathologicStruc") == "[1]"
    assert one_trgt_variant.format("MC") == "12_0"

    # GIVEN a random individual - the keys will be used, not the id - and assuming pos 0 for a singleton.
    pos = 0
    gt_call = parse_genotype(one_trgt_variant, one_individual, pos)

    # THEN the correct, second motif MC will be returned
    assert gt_call["alt_mc"] == 0


@pytest.mark.parametrize(
    "format_keys, format_dict, expected",
    [
        (["GT"], {}, None),
        (["CN"], {"CN": [[None]]}, None),
        (["CN"], {"CN": [[-1]]}, None),
        (["CN"], {"CN": [[4]]}, 4),
    ],
)
def test_get_copy_number(format_keys, format_dict, expected):
    """Test extraction of copy number from SV variant using an in-test FakeVariant."""

    class FakeVariant:
        def __init__(self, format_keys, format_dict):
            self.FORMAT = format_keys
            self._format_dict = format_dict

        def get_format(self, key):
            return self._format_dict.get(key, [])

    variant = FakeVariant(format_keys, format_dict)

    # Monkeypatch get_copy_number to call get_format instead of format
    variant.format = variant.get_format

    result = get_copy_number(variant, 0)

    assert result == expected


@pytest.mark.parametrize(
    "raw_gt, expected_alleles, expected_phased",
    [
        ([-1, False, -2], [-1], False),
        ([0, 1, True], [0, 1], True),
        ([1, -1, False], [1, -1], False),
    ],
)
def test_extract_genotype_alleles_mixed_ploidy_padding(raw_gt, expected_alleles, expected_phased):
    """cyvcf2 may place phase before trailing filler values for mixed ploidy."""
    alleles, phased = _extract_genotype_alleles(raw_gt)
    assert alleles == expected_alleles
    assert phased is expected_phased


def test_parse_genotype_haploid_missing_gt_padding():
    """Ensure padded haploid missing GT does not become 0/0 due to bool/int coercion."""

    class FakeVariant:
        FORMAT = ["GT"]

        def __init__(self):
            self.genotypes = [[-1, False, -2]]
            self.gt_phases = [False]
            self.gt_alt_depths = [-1]
            self.gt_ref_depths = [-1]
            self.gt_depths = [0]
            self.gt_alt_freqs = [0.0]
            self.gt_quals = [0]
            self.INFO = {}

        def format(self, _key):
            raise KeyError("No FORMAT entries available in this fake variant")

    ind = {"individual_id": "sample", "display_name": "sample"}

    gt_call = parse_genotype(FakeVariant(), ind, 0)

    assert gt_call["genotype_call"] == "."


def test_parse_trgt_mc_ignores_phase_slot_in_haploid_padding():
    """Do not treat phase boolean as a reference allele in padded haploid GT arrays."""

    class FakeInfo(dict):
        pass

    class FakeVariant:
        FORMAT = ["MC"]

        def __init__(self):
            self.genotypes = [[1, False, -2]]
            self.INFO = FakeInfo()

        def format(self, key):
            if key == "MC":
                return ["5,8"]
            raise KeyError(key)

    mc_ref, mc_alt = _parse_format_entry_trgt_mc(FakeVariant(), 0)

    assert mc_ref is None
    assert mc_alt == 8
