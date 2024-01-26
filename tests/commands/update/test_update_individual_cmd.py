"""Tests for update individual command"""
import pytest
from click.testing import CliRunner

from scout.commands.update.individual import UPDATE_DICT
from scout.commands.update.individual import individual as ind_cmd


def test_update_individual_no_args():
    """Tests the CLI that updates a individual"""

    # GIVEN a CLI object
    runner = CliRunner()

    # WHEN updating a individual without any args
    result = runner.invoke(ind_cmd)

    # THEN assert it fails since its missing mandatory arguments
    assert result.exit_code == 2
    assert "Missing option" in result.output


def test_update_individual_non_existing_case(empty_mock_app):
    """Tests the CLI that updates an individual from a case that doesn't exist"""

    case_id = "acase"
    ind_id = "anind"
    # GIVEN a CLI object
    runner = empty_mock_app.test_cli_runner()

    # WHEN updating a individual without a valid case
    result = runner.invoke(ind_cmd, ["--case-id", case_id, "--ind", ind_id])

    # THEN assert it exits
    assert result.exit_code == 0
    # With a pertinent message
    assert "Could not find case" in result.output


def test_update_individual_no_individual(empty_mock_app, real_adapter, case_obj):
    """Tests the CLI that updates a individual with case id and no ind name"""

    # GIVEN a CLI object
    runner = empty_mock_app.test_cli_runner()

    real_adapter.case_collection.insert_one(case_obj)
    assert real_adapter.case_collection.find_one()

    # WHEN updating a individual providing the wrong individual name or no individual name
    result = runner.invoke(ind_cmd, ["--case-id", case_obj["_id"]])

    # THEN assert it exits
    assert result.exit_code == 0
    # With a pertinent message
    assert "Please specify individual name" in result.output


def test_update_individual_no_update_key(empty_mock_app, real_adapter, case_obj):
    """Tests the CLI that updates a individual without providing a valid key"""

    # GIVEN a CLI object
    runner = empty_mock_app.test_cli_runner()

    real_adapter.case_collection.insert_one(case_obj)
    assert real_adapter.case_collection.find_one()

    ind_name = case_obj["individuals"][0]["display_name"]

    # WHEN updating a individual without a valid key
    result = runner.invoke(ind_cmd, ["--case-id", case_obj["_id"], "--ind", ind_name])

    # THEN assert it exits
    assert result.exit_code == 0
    # With a pertinent message
    assert "Please specify a valid key" in result.output


def test_update_key_non_existent_path(mock_app, real_populated_database, case_obj):
    """Tests the CLI that updates a individual with an alignment path that is nit found on the server"""

    # GIVEN a CLI object
    runner = mock_app.test_cli_runner()
    # GIVEN a database with a case_obj
    existing_case = real_populated_database.case_collection.find_one()
    case_id = existing_case["_id"]
    ind_info = existing_case["individuals"][0]
    ind_name = ind_info["display_name"]

    # WHEN updating a individual without a valid alignment path
    result = runner.invoke(
        ind_cmd,
        ["--case-id", case_id, "--ind", ind_name, "bam_file", "not_a_valid_path"],
    )

    # THEN the command should ask user to confirm save action
    assert result.exit_code == 1
    assert "The provided path was not found on the server, update key anyway?" in result.output


@pytest.mark.parametrize("update_key", UPDATE_DICT)
def test_update_individuals_key_value(
    mock_app, real_populated_database, update_key, custom_temp_file
):
    """Tests the CLI that updates case individual's key/values."""

    # GIVEN a CLI object
    runner = mock_app.test_cli_runner()
    # GIVEN a database with a case_obj
    existing_case = real_populated_database.case_collection.find_one()
    case_id = existing_case["_id"]
    ind_info = existing_case["individuals"][0]
    ind_name = ind_info["display_name"]

    # GIVEN a value for the key to be updated
    update_value = str(custom_temp_file(".xyz"))

    # WHEN updating a individual with a valid key/value
    result = runner.invoke(
        ind_cmd,
        ["--case-id", case_id, "--ind", ind_name, update_key, update_value],
    )

    # THEN the command should run with no errors
    assert result.exit_code == 0

    # THEN the individual should be updated
    fetched_case = real_populated_database.case_collection.find_one()
    if "." in update_key:
        update_key_values = update_key.split(".")
        assert (
            fetched_case["individuals"][0][update_key_values[0]][update_key_values[1]]
            == update_value
        )
    else:
        assert fetched_case["individuals"][0][update_key] == update_value
