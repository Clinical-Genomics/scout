import pytest

from scout.commands import cli
from scout import __version__
from flask.cli import current_app

#Sanity check for cli
def test_base_cmd(mock_app):

    runner = mock_app.test_cli_runner()
    assert runner

    # test scout -v command
    result =  runner.invoke(cli, ['--loglevel', 'DEBUG', '-v'])
    assert result.exit_code == 0
    assert 'Running scout version {}'.format(__version__) in result.output

    # test setting the database to scout-demo using the CLI
    result = runner.invoke(cli, ['--demo', 'view', 'institutes'])
    assert result.exit_code == 0
