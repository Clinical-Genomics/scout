# -*- coding: utf-8 -*-

from scout.commands import app_cli

def test_update_diseases(mock_app):
    """Tests the CLI that updates OMIM terms in database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(app_cli, ['update', 'diseases'])
    assert 'INFO Fetching OMIM files from https://omim' in result.output
    # command raises error because no valid key is provided
    assert result.exit_code != 0
