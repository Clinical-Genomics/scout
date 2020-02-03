# -*- coding: utf-8 -*-

import os
import pytest
import shutil
import tempfile
from scout.demo import load_path

from scout.commands import cli
from scout.server.extensions import store


def test_load_case(mock_app, institute_obj, case_obj):
    """Testing the scout load case command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # remove case from real populated database using adapter
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None
    res = store.institute_collection.find({"_id": "cust000"})
    assert sum(1 for i in res) == 1

    # Make sure the scout config file is available
    assert os.path.exists(load_path)

    # Test command to upload case using demo resources:
    result = runner.invoke(cli, ["load", "case", load_path])
    assert result.exit_code == 0
    assert sum(1 for i in store.case_collection.find()) == 1


def test_load_case_KeyError(mock_app, institute_obj, case_obj):
    # GIVEN a config setup with 'sample_id' missing
    runner = mock_app.test_cli_runner()
    assert runner

    # remove case from real populated database using adapter
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None
    res = store.institute_collection.find({"_id": "cust000"})
    assert sum(1 for i in res) == 1

    # Make sure the scout config file is available
    assert os.path.exists(load_path)
    temp_conf = os.path.join(tempfile.gettempdir(), "temp.conf")
    shutil.copy2(load_path, temp_conf)
    sed_change = "sed -i -e 's/sample_id/SAMPLE_ID/g' "
    os.system(sed_change + temp_conf)

    # WHEN: config is loaded
    result = runner.invoke(cli, ["load", "case", temp_conf])
    # THEN KeyError is caught and exit value is non-zero
    assert result.exit_code != 0
    os.remove(temp_conf)  # clean up


def test_load_case_NoConf(mock_app, institute_obj, case_obj):
    # GIVEN a load command missing path to config
    runner = mock_app.test_cli_runner()
    assert runner

    # remove case from real populated database using adapter
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None
    res = store.institute_collection.find({"_id": "cust000"})
    assert sum(1 for i in res) == 1
    no_load_path = ""

    # WHEN load command is run
    result = runner.invoke(cli, ["load", "case", no_load_path])

    # THEN error in exit status
    assert result.exit_code != 0
