# -*- coding: utf-8 -*-
import os
import tempfile

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


def test_load_case_from_yaml(mock_app, institute_obj, case_obj):
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


def test_load_case_key_error(mock_app, institute_obj, case_obj, monkeypatch):
    """Test loading a case with a config file that will trigger keyError"""

    runner = mock_app.test_cli_runner()

    # GIVEN a patched scout add_smn_info function that will raise KeyError
    def mock_smn_info(*args):  # noqa
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
    assert "KeyError" in result.output


def test_load_case_syntax_error(mock_app, institute_obj, case_obj, monkeypatch):
    """Test loading a case with a config file that will trigger KeyError"""
    runner = mock_app.test_cli_runner()

    # GIVEN a patched `parse_case` function that will raise KeyError
    def mock_parse_case(*args):  # noqa
        raise SyntaxError

    monkeypatch.setattr(case, "add_smn_info", mock_parse_case)

    # GIVEN a database with no cases
    store.delete_case(case_id=case_obj["_id"])
    assert store.case_collection.find_one() is None

    # WHEN case is loaded using a a yaml file
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["load", "case", load_path])

    # THEN call will fail with KeyError
    assert result.exit_code == 1
    assert "SyntaxError" in result.output


def test_load_case_key_missing(mock_app, institute_obj, case_obj):
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


def test_load_case_no_config(mock_app, institute_obj, case_obj):
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


def test_load_case_bad_path(mock_app, institute_obj, case_obj):
    # GIVEN a config setup with an incorrect path configured
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
    content.remove("vcf_snv: scout/demo/643594.clinical.vcf.gz\n")
    content.append("vcf_snv: scout/demo/incorrect_path/643594.clinical.vcf.gz\n")

    with open(temp_conf, mode="wt") as f:
        f.write("".join(content))

    # WHEN: config is loaded
    result = runner.invoke(cli, ["load", "case", temp_conf])
    # THEN KeyError is caught and exit value is non-zero
    assert result.exit_code == 1
