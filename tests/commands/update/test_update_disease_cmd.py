# -*- coding: utf-8 -*-

from scout.commands import cli


def test_update_diseases(mock_app):
    """Tests the CLI that updates disease terms in database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "diseases"])
    assert "WARNING Please provide a omim api key to load the omim gene panel" in result.output
    # command raises error because no valid key is provided
    assert result.exit_code != 0
