# -*- coding: utf-8 -*-

from scout.constants.variants_export import MT_EXPORT_HEADER
from scout.export.variant import export_mt_variants


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
