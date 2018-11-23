import click
from click.testing import CliRunner
from scout.commands import cli
from scout.export.variant import export_mt_variants
from scout.constants.variants_export import MT_EXPORT_HEADER

def test_export_mt_report(real_populated_database):
    adapter = real_populated_database
    case_id = adapter.case_collection.find_one()['_id']
    case_obj = adapter.case(case_id=case_id)
    assert case_obj

    # load variants for this case
    nr_loaded = adapter.load_variants(case_obj=case_obj,
                          category='snv', chrom='MT', start=1, end=16500)
    assert nr_loaded > 0
    mt_variants = list(adapter.variant_collection.find({'chromosome':'MT'}))
    assert len(mt_variants) == nr_loaded # it's all MT variants

    # Assert that there is at least one sample to create the excel file for
    samples = case_obj.get('individuals')
    assert samples

    # test function that exports variant lines
    for sample in samples:
        sample_id = sample['individual_id']
        sample_lines = export_mt_variants(variants=mt_variants, sample_id=sample_id)

        # check that rows to write to excel corespond to number of variants
        assert len(sample_lines) == len(mt_variants)
        # check that cols to write to excel corespond to fields of excel header
        assert len(sample_lines[0]) == len(MT_EXPORT_HEADER)

    # test that the cli that uses the function above works when invoked with the right options
    runner = CliRunner()
    result = runner.invoke(cli, ['export', 'mt_report', '--case_id', case_id, '--test'])
    assert result.exit_code == 0
