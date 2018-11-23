import click
from click.testing import CliRunner
from scout.commands import cli
from scout.export.variant import export_mt_variants

def test_export_mt_report(real_populated_database, case_obj):

    adapter = real_populated_database
    case_id = case_obj['_id']
    assert case_id

    # test that the cli works when invoked with the right options
    runner = CliRunner()
    result = runner.invoke(cli, ['export', 'mt_report', '--case-id', case_id, '--test'])
    assert result.exit_code == 0
