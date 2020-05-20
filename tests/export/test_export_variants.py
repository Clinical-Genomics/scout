# -*- coding: utf-8 -*-

from scout.export.variant import export_mt_variants, export_verified_variants
from scout.constants.variants_export import MT_EXPORT_HEADER, VERIFIED_VARIANTS_HEADER
from scout.constants import CALLERS


def test_export_mt_variants(case_obj, real_populated_database):
    """Test the function that creates lines with MT variants to be exported"""
    adapter = real_populated_database
    case_id = case_obj["_id"]
    assert case_id

    # load MT variants for this case
    nr_loaded = adapter.load_variants(
        case_obj=case_obj, category="snv", chrom="MT", start=1, end=16500
    )
    assert nr_loaded > 0
    mt_variants = list(adapter.variant_collection.find({"chromosome": "MT"}))
    assert len(mt_variants) == nr_loaded  # it's all MT variants, but double-checking it

    # Assert that there is at least one sample to create the excel file for
    samples = case_obj.get("individuals")
    assert samples

    # test function that exports variant lines
    for sample in samples:
        sample_lines = export_mt_variants(variants=mt_variants, sample_id=sample["individual_id"])

        # check that rows to write to excel corespond to number of variants
        assert len(sample_lines) == len(mt_variants)
        # check that cols to write to excel corespond to fields of excel header
        assert len(sample_lines[0]) == len(MT_EXPORT_HEADER)


def test_export_verified_variants(case_obj, real_populated_database, variant_objs):
    """Test the function that creates lines with verified variants to be exported"""

    adapter = real_populated_database
    case_id = case_obj["_id"]

    # load variants to populated_database
    assert sum(1 for i in adapter.variants(case_id=case_id, nr_of_variants=-1)) == 0
    nr_loaded = adapter.load_variants(case_obj=case_obj)
    assert nr_loaded > 0

    valid_status = ["False positive", "True positive", "False positive"]  # for 3 vars

    test_vars = list(adapter.variant_collection.find().limit(3))
    assert len(test_vars) == 3

    # Make sure that no variant is set as validated:
    assert sum(1 for i in adapter.variant_collection.find({"validation": {"$exists": True}})) == 0

    # Set test variant as validated
    for i in range(3):
        # Set validation status of a variant
        adapter.variant_collection.find_one_and_update(
            {"_id": test_vars[i]["_id"]}, {"$set": {"validation": valid_status[i]}}
        )

        # insert validation events
        adapter.event_collection.insert_one(
            {
                "verb": "validate",
                "institute": test_vars[i]["institute"],
                "variant_id": test_vars[i]["variant_id"],
                "case": case_id,
            }
        )

    # There should be 3 validated variants now
    assert sum(1 for i in adapter.variant_collection.find({"validation": {"$exists": True}})) == 3

    # Call function to get aggregated data (variant + case data):
    cust = case_obj["owner"]
    aggregated_vars = adapter.verified(cust)
    assert len(aggregated_vars) == 3  # same number of variants is returned

    unique_callers = set()
    for var_type, var_callers in CALLERS.items():
        for caller in var_callers:
            unique_callers.add(caller.get("id"))

    n_individuals = len(case_obj["individuals"])

    # Call function that creates document lines
    document_lines = export_verified_variants(aggregated_vars, unique_callers)
    assert len(document_lines) == 3 * n_individuals  # one line per variant and individual

    for line in document_lines:
        # Make sure that document cells will be the same as in document header
        assert len(line) == len(VERIFIED_VARIANTS_HEADER + list(unique_callers))
