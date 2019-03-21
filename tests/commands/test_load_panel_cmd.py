# -*- coding: utf-8 -*-

from scout.commands import app_cli
from scout.server.extensions import store

def test_load_institute(mock_app, institute_obj):
    """Test the CLI commands that loads a gene panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    assert store.panel_collection.find().count() == 1

    # Modify existing panel ID into OMIM-AUTO, so cli runner will not add it again
    store.panel_collection.find_one_and_update({'panel_name':'panel1'},{'$set': {'panel_name':'OMIM-AUTO'}})

    # Test CLI by passing the panel 'OMIM-AUTO':
    result =  runner.invoke(app_cli, ['load', 'panel',
        '--api-key', mock_app.config.get('OMIM_API_KEY'),
        '--omim'])
    assert 'OMIM-AUTO already exists in database' in result.output
