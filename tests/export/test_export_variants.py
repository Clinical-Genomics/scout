import responses

from scout.constants.managed_variant import MANAGED_VARIANTS_INFILE_HEADER
from scout.constants.variants_export import MT_EXPORT_HEADER
from scout.export.variant import export_lift_over_managed_variants, export_mt_variants
from scout.utils.broad_liftover_client import LIFTOVER_URL


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
def test_export_lift_over_managed_variants(broad_bcftools_liftover_response, capsys):
    """Test the function lifts over and formats managed variants into a managed variants infile."""

    # GIVEN an Iterable with managed variants:
    managed_variant = {
        "chromosome": "8",
        "position": 141310715,
        "end": 141310715,
        "reference": "T",
        "alternative": "G",
        "category": "snv",
        "build": "37",
    }

    managed_variants = [managed_variant]

    url = (
        f"{LIFTOVER_URL}/"
        "?hg=hg19-to-hg38"
        "&format=variant"
        f"&chrom={managed_variant['chromosome']}"
        f"&pos={managed_variant['position']}"
        f"&end={managed_variant['end']}"
        f"&ref={managed_variant['reference']}"
        f"&alt={managed_variant['alternative']}"
    )

    # GIVEN a mocked call to the liftover service (BCFTools via Broad institute's API)
    resp = broad_bcftools_liftover_response
    responses.add(
        responses.GET,
        url,
        json=resp,
        status=200,
    )

    # WHEN exporting the managed variants
    export_lift_over_managed_variants(
        managed_variants=managed_variants,
        liftover_from="37",
    )

    # THEN a header and a lifted variant line should be printed
    out = capsys.readouterr().out.splitlines()

    assert out[0] == MANAGED_VARIANTS_INFILE_HEADER
    assert (
        out[1]
        == f"{resp['chrom'].replace('chr','')};{resp['output_pos']};{resp['output_pos']};{resp['output_ref']};{resp['output_alt']};snv;snv;38;None (managed, build37);;"
    )
