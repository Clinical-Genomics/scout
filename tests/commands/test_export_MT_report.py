import os
from scout.commands import cli
from click.testing import CliRunner

def test_export_mt_report(case_obj, real_populated_database):

    case_id = case_obj['_id']
    assert case_id
    adapter = real_populated_database

    runner = CliRunner()
    # invoke the cli with all the args required to test the creation of 3 MT files
    result = runner.invoke(cli, ['export', 'mt_report', '--case_id', case_id, '--test'])

    # check that the simulation would create 3 files
    assert ''.join(['Number of excel files that can be written to folder ', os.getcwd(), ': 3']) in result.output
