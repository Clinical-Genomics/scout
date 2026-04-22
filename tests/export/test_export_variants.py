# -*- coding: utf-8 -*-

import responses

from scout.constants.managed_variant import MANAGED_VARIANTS_INFILE_HEADER
from scout.constants.variants_export import MT_EXPORT_HEADER
from scout.export.variant import export_mt_variants, liftover_managed_variants
from scout.utils.ensembl_rest_clients import RESTAPI_URL


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

        # check that rows to write to excel correspond to number of variants
        assert len(sample_lines) == len(mt_variants)
        # check that cols to write to excel correspond to fields of Excel header
        assert len(sample_lines[0]) == len(MT_EXPORT_HEADER)


@responses.activate
def test_liftover_managed_variants(ensembl_liftover_response):
    """Test the function that performs liftover over a list of managed variants and formats them into a list of strings."""

    # GIVEN a patched response from Ensembl
    url = f"{RESTAPI_URL}/map/human/GRCh37/X:1000000..1000000/GRCh38?content-type=application/json"
    responses.add(
        responses.GET,
        url,
        json=ensembl_liftover_response,
        status=200,
    )
    managed_variant_info = {
        "chromosome": "X",
        "position": "1000000",
        "reference": "C",
        "alternative": "T",
        "build": "37",
    }

    # GIVEN a list of managed variants
    managed_variants = [managed_variant_info]

    # THEN the liftover function should export them correctly:
    export_lines = liftover_managed_variants([var for var in managed_variants], liftover_from="37")

    # WITH the first line being the header
    assert export_lines[0] == MANAGED_VARIANTS_INFILE_HEADER

    # AND second line being the lifted-over variant
    lifted_chrom = ensembl_liftover_response["mappings"][0]["mapped"]["seq_region_name"]
    lifted_position = ensembl_liftover_response["mappings"][0]["mapped"]["start"]
    lifted_end = ensembl_liftover_response["mappings"][0]["mapped"]["end"]
    assert f"{lifted_chrom};{lifted_position};{lifted_end}" in export_lines[1]
