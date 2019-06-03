# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store
from scout.demo import panel_path

def test_convert(mock_app):
    """Test the CLI command that converts a gene panel with hgnc symbols
    to a new one with hgnc ids"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without providing panel file
    result =  runner.invoke(cli, ['convert'])

    # It should return error message
    assert 'Missing argument "panel"' in result.output

    # Provide a non-valid path to a panel file
    result =  runner.invoke(cli, ['convert',
        'wrong/path/to/file'])
    assert result.exit_code != 0
    assert 'Invalid value for "panel": Could not open file: wrong/path/to/file:' in result.output

    # Provide a valid path to a panel file
    result =  runner.invoke(cli, ['convert',
        panel_path])
    # genes should be converted as expected
    assert result.exit_code == 0
    assert '2397\tCRYBB1\t\t\t\t\t\n9394\tPICK1' in result.output
