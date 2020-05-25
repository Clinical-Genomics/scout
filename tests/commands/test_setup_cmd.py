# -*- coding: utf-8 -*-
from scout.commands import cli


def test_setup_database_invalid_omim_key(mock_app):
    """Testing the cli to setup a full scale database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command with non-valid API key
    result = runner.invoke(cli, ["setup", "database", "--api-key", "not_a_valid_key", "--yes"])
    # Make sure that setup enters in setup function correctly but stops because
    # there is no valid OMIM API KEY
    assert result.exit_code != 0


def test_setup_database(mock_app):
    """Testing the cli to setup a full scale database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command for seting up scout
    result = runner.invoke(cli, ["setup", "demo"])

    # Make sure that setup function works correctly
    assert result.exit_code == 0
    assert "Scout instance setup successful" in result.output
