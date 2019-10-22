# -*- coding: utf-8 -*-

from scout.commands import cli

def test_update_genes_wrong_omim_key(mock_app):
    """Tests the CLI that updates genes in database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, provide non-valid API key
    result =  runner.invoke(cli, ['update', 'genes',
        '--api-key', 'not_a_valid_key'
    ])
    assert 'Seems like url https://data.omim.org/downloads/not_a_valid_key/morbidmap.txt does not exist' in result.output
