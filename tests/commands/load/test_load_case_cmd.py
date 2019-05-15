# -*- coding: utf-8 -*-

import os
from scout.demo import load_path

from scout.commands import cli
from scout.server.extensions import store

def test_load_case(mock_app, institute_obj, case_obj):
    """Testing the scout load case command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # remove case from real populated database using adapter
    store.delete_case(case_id=case_obj['_id'])
    assert store.case_collection.find().count() == 0
    assert store.institute_collection.find({'_id':'cust000'}).count()==1

    # Make sure the scout config file is available
    assert os.path.exists(load_path)

    # Test command to upload case using demo resources:
    result =  runner.invoke(cli, ['load', 'case', load_path ])
    assert result.exit_code == 0
    assert store.case_collection.find().count() == 1
