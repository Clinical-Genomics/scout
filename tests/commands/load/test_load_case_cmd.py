# -*- coding: utf-8 -*-

import os
import pytest
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
    result = runner.invoke(cli, ['load', 'case', load_path ])
    assert result.exit_code == 0
    assert store.case_collection.find().count() == 1




def test_load_case_KeyError(mock_app, institute_obj, case_obj):
    # GIVEN a config setup with 'sample_id' missing
    runner = mock_app.test_cli_runner()
    assert runner

    # remove case from real populated database using adapter
    store.delete_case(case_id=case_obj['_id'])
    assert store.case_collection.find().count() == 0
    assert store.institute_collection.find({'_id':'cust000'}).count()==1

    # Make sure the scout config file is available
    assert os.path.exists(load_path)
    sed_change = "sed -i -e 's/sample_id/SAMPLE_ID/g' "
    os.system(sed_change + load_path)    

    # Test command to upload case using demo resources:
    # WHEN: config is loaded
    result = runner.invoke(cli, ['load', 'case', load_path ])
    # THEN KeyError is caught and exit value is non-zero
    assert result.exit_code != 0

    sed_restore = "sed -i -e 's/SAMPLE_ID/sample_id/g' "    # restore config
    os.system(sed_restore + load_path)    

    
def test_load_case_NoConf(mock_app, institute_obj, case_obj):
    # GIVEN a load command missing path to config
    runner = mock_app.test_cli_runner()
    assert runner

    # remove case from real populated database using adapter
    store.delete_case(case_id=case_obj['_id'])
    assert store.case_collection.find().count() == 0
    assert store.institute_collection.find({'_id':'cust000'}).count()==1
    no_load_path = ""

    # WHEN load command is run
    result = runner.invoke(cli, ['load', 'case', no_load_path ])

    # THEN error in exit status
    assert result.exit_code != 0



