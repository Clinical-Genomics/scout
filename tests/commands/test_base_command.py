import pytest

from scout.commands import app_cli
from flask.cli import current_app

#Sanity check for cli
def test_version(mock_app):

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(app_cli, [])
    assert result.exit_code == 0
    assert 'Entry point of Scout CLI' in result.output

    # Test changing log level using loglevel param
    result =  runner.invoke(app_cli, ['--loglevel', 'DEBUG', '--help'])
    assert result.exit_code == 0
    assert 'Running scout version' not in result.output

    # test setting the database to scout-demo using the CLI
    result = runner.invoke(app_cli, ['--demo', 'view', 'institutes'])
    assert 'setting up connection to use database:"scout-demo"' in result.output
