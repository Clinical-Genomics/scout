# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store

def test_load_institute(mock_app, institute_obj):
    """Testing the load institute cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # One institute is preloaded into populated database
    assert sum(1 for i in store.institute_collection.find()) == 1

    # remove it
    store.institute_collection.find_one_and_delete({'_id':institute_obj['_id']})
    assert store.institute_collection.find_one() is None

    # and re-load it using the CLI command:
    result =  runner.invoke(cli, ['load', 'institute',
        '-i', institute_obj['_id'], '-d', institute_obj['display_name'],
        '-s', institute_obj['sanger_recipients']])

    # CLI command should be exit with no errors
    assert result.exit_code == 0

    # and institute should be in database
    assert sum(1 for i in store.institute_collection.find()) == 1
