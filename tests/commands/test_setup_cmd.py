# -*- coding: utf-8 -*-

from scout.commands import app_cli

def test_setup_database(mock_app):
    """Testing the cli to setup a full scale database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command:
    result =  runner.invoke(app_cli, ['setup', 'database'], input='y')

    # Make sure that setup enters in setup function correctly but stops because there is no valid OMIM API KEY
    assert 'Seems like url https://data.omim.org/downloads/omim_api_key/morbidmap.txt does not exist' in result.output
