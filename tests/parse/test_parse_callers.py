import pytest

from scout.constants import CALLERS
from scout.parse.variant.callers import parse_callers


def test_parse_callers(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that gatk and freebayes have passed
    variant.INFO["set"] = "gatk-freebayes"

    # WHEN parsing the information
    callers = parse_callers(variant)

    # THEN the correct callers should be passed
    assert callers["gatk"] == "Pass"
    assert callers["freebayes"] == "Pass"
    assert callers["samtools"] == None


def test_parse_callers_only_one(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information about the variant callers
    variant.INFO["set"] = "gatk"

    # WHEN parsing the information
    callers = parse_callers(variant)

    # THEN the correct callers should be passed
    assert callers["gatk"] == "Pass"
    assert callers["freebayes"] == None
    assert callers["samtools"] == None


def test_parse_callers_complex(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information about the variant callers
    variant.INFO["set"] = "gatk-filterInsamtools-freebayes"

    # WHEN parsing the information
    callers = parse_callers(variant)

    # THEN the correct output should be returned
    assert callers["gatk"] == "Pass"
    assert callers["freebayes"] == "Pass"
    assert callers["samtools"] == "Filtered"


def test_parse_callers_intersection(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that all callers agree on Pass
    variant.INFO["set"] = "Intersection"

    # WHEN parsing the information
    callers = parse_callers(variant)

    # THEN all callers should be passed
    assert callers["gatk"] == "Pass"
    assert callers["freebayes"] == "Pass"
    assert callers["samtools"] == "Pass"


def test_parse_callers_intersection_svdb_info(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that all callers agree on Pass
    variant.INFO["svdb_origin"] = "gatk|deepvariant"
    variant.INFO["set"] = "Intersection"

    # WHEN parsing the information
    callers = parse_callers(variant)

    # THEN the svdb info selected callers should be passed
    assert callers["gatk"] == "Pass"
    assert callers["deepvariant"] == "Pass"
    assert callers["samtools"] is None


def test_parse_callers_filtered_all(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that all callers agree on filtered
    variant.INFO["set"] = "FilteredInAll"

    # WHEN parsing the information
    callers = parse_callers(variant)

    # THEN all callers should be filtered
    assert callers["gatk"] == "Filtered"
    assert callers["freebayes"] == "Filtered"
    assert callers["samtools"] == "Filtered"


def test_parse_sv_callers_filtered_all(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that all callers agree on filtered
    variant.INFO["set"] = "FilteredInAll"

    # WHEN parsing the information
    callers = parse_callers(variant, category="sv")

    # THEN all callers should be filtered
    assert callers["cnvnator"] == "Filtered"
    assert callers["delly"] == "Filtered"
    assert callers["tiddit"] == "Filtered"
    assert callers["manta"] == "Filtered"


def test_parse_sv_callers_intersection(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that all callers agree on filtered
    variant.INFO["set"] = "Intersection"

    # WHEN parsing the information
    callers = parse_callers(variant, category="sv")

    # THEN all callers should be filtered
    assert callers["cnvnator"] == "Pass"
    assert callers["delly"] == "Pass"
    assert callers["tiddit"] == "Pass"
    assert callers["manta"] == "Pass"


def test_parse_sv_callers_filterin_tiddit(cyvcf2_variant):
    variant = cyvcf2_variant
    # GIVEN information that all callers agree on filtered
    variant.INFO["set"] = "manta-filterIntiddit"

    # WHEN parsing the information
    callers = parse_callers(variant, category="sv")

    # THEN all callers should be filtered
    assert callers["cnvnator"] == None
    assert callers["delly"] == None
    assert callers["tiddit"] == "Filtered"
    assert callers["manta"] == "Pass"


def test_parse_callers(one_vep104_annotated_variant):
    variant = one_vep104_annotated_variant

    assert variant.INFO["FOUND_IN"] == "deepvariant"

    # WHEN parsing the caller info
    callers = parse_callers(variant, category="snv")
    # THEN the deep variant caller should be found, but not GATK
    assert callers["deepvariant"] == "Pass"
    assert callers["gatk"] == None


@pytest.mark.parametrize("category", ["snv", "sv", "cancer", "cancer_sv"])
def test_parse_callers_all(cyvcf2_variant, category):
    # GIVEN all callers called a cancer variant
    variant = cyvcf2_variant
    variant.INFO["set"] = "Intersection"
    # WHEN parsing callers
    parsed_callers = parse_callers(variant, category=category)
    # THEN all callers should be in the dict
    legal_callers = set(caller["id"] for caller in CALLERS[category])
    assert legal_callers == set(parsed_callers.keys())
