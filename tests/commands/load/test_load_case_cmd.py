# -*- coding: utf-8 -*-
import os
import tempfile

import pytest

from scout.commands import cli
from scout.demo import load_path, ped_path
from scout.parse import case
from scout.server.extensions import store


def test_load_case_no_yaml_no_ped(mock_app, institute_obj):
    """Test loading a case into scout without any config file"""

    case_owner = institute_obj["_id"]

    # WHEN case is loaded without any config file
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["load", "case", "--owner", case_owner])
    # THEN it should return error
    assert result.exit_code != 0
    assert "Please provide either scout config or ped" in result.output


def test_load_case_from_ped(mock_app, institute_obj, case_obj):
    """Test loading a case into scout from a ped file. It requires providing case genome build in the prompt."""

    # GIVEN a database with no cases
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None

    case_owner = institute_obj["_id"]

    # WHEN case is loaded using a ped file it will also require a genome build
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "case", "--owner", case_owner, "--ped", ped_path], input="37"
    )

    # THEN case should be saved correctly
    assert result.exit_code == 0
    case_obj = store.case_collection.find_one()
    # WITH the expected genome build
    assert case_obj["genome_build"] == 37


def test_load_case_from_yaml_keys(mock_app, institute_obj, case_obj, demo_case_keys):
    """Testing loaded case contains expected keys when loaded using yaml file"""

    runner = mock_app.test_cli_runner()

    # GIVEN a database with no cases
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None

    # GIVEN that the database contains cases HPO terms:
    hpo_terms = [
        {"_id": "HP:0001298", "hpo_id": "HP:0001298", "description": "Encephalopathy"},
        {"_id": "HP:0001250", "hpo_id": "HP:0001250", "description": "Seizures"},
    ]
    store.hpo_term_collection.insert_many(hpo_terms)

    # WHEN a case is loaded using a yaml config file
    result = runner.invoke(cli, ["load", "case", load_path])

    # THEN the command should be successful
    assert result.exit_code == 0

    # AND the case should be saved in database
    new_case = store.case_collection.find_one()
    assert new_case

    # WHEN case is loaded it should contain the expected fields:
    for key in demo_case_keys:
        key_value_expected = f"{key}->True"
        key_value = "{key}->{bool_value}"

        # Some fields might be boolean False values
        if key in ["is_research", "research_requested", "rerun_requested", "is_migrated"]:
            assert (
                key_value.format(key=key, bool_value=new_case[key] is False) == key_value_expected
            )
        # Some fields might not have values:
        elif key in ["multiqc", "cnv_report", "coverage_qc_report", "gene_fusion_report_research"]:
            assert key_value.format(key=key, bool_value=new_case[key] is None) == key_value_expected

        # Some other keys might be empty lists
        elif key in ["dynamic_gene_list", "group"]:
            assert (
                key_value.format(key=key, bool_value=len(new_case[key]) == 0) == key_value_expected
            )
        else:
            assert key_value.format(key=key, bool_value=bool(new_case[key])) == key_value_expected


def test_load_case_KeyError(mock_app, institute_obj, case_obj, monkeypatch):
    """Test loading a case with a config file that will trigger keyError"""

    runner = mock_app.test_cli_runner()

    # GIVEN a patched scout add_smn_info function that will raise KeyError
    def mock_smn_info(*args):
        raise KeyError

    monkeypatch.setattr(case, "add_smn_info", mock_smn_info)

    # GIVEN a database with no cases
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None

    # WHEN case is loaded using a a yaml file
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["load", "case", load_path])

    # THEN it should trigger KeyError
    assert result.exit_code == 1
    assert "KEYERROR" in result.output


def test_load_case_KeyMissing(mock_app, institute_obj, case_obj):
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

    content = []
    with open(load_path) as f:
        content = f.readlines()

    # Remove a mandatory key value from config value content
    content.remove("family: 'internal_id'\n")

    with open(temp_conf, mode="wt") as f:
        f.write("".join(content))

    # WHEN: config is loaded
    result = runner.invoke(cli, ["load", "case", temp_conf])
    # THEN KeyError is caught and exit value is non-zero
    assert result.exit_code != 0


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
