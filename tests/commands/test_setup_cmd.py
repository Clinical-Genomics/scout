# -*- coding: utf-8 -*-

from scout.commands import cli

def test_setup_database(mock_app):
    """Testing the cli to setup a full scale database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command:
    result =  runner.invoke(cli, ['setup', 'database'], input='y')
    # It should fail because no OMIM API key is provided
    assert 'Please provide a omim api key with --api-key' in result.output

    # test the CLI command with non-valid API key
    result =  runner.invoke(cli, ['setup', 'database',
        '--api-key', 'not_a_valid_key'], input='y')
    # Make sure that setup enters in setup function correctly but stops because
    # there is no valid OMIM API KEY
    assert 'Seems like url https://data.omim.org/downloads/not_a_valid_key/morbidmap.txt does not exist' in result.output
