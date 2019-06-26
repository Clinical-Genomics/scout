# -*- coding: utf-8 -*-

from scout.commands import cli

def test_update_genes(mock_app):
    """Tests the CLI that updates genes in database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(cli, ['update', 'genes'])
    assert 'Please provide a omim api key to load the omim gene panel' in result.output
    # command raises error because no valid key is provided
    assert result.exit_code != 0

    # Test CLI base, provide non-valid API key
    result =  runner.invoke(cli, ['update', 'genes',
        '--api-key', 'not_a_valid_key'
    ])
    assert 'Seems like url https://data.omim.org/downloads/not_a_valid_key/morbidmap.txt does not exist' in result.output
