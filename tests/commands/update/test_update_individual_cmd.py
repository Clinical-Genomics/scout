"""Tests for update individual command"""

from click.testing import CliRunner

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


def test_update_alignment_path(mock_app, real_populated_database, bam_path):
    """Tests the CLI that updates a individual with an alignment path"""

    # GIVEN a CLI object
    runner = mock_app.test_cli_runner()
    # GIVEN a database with a case_obj
    existing_case = real_populated_database.case_collection.find_one()
    case_id = existing_case["_id"]
    ind_info = existing_case["individuals"][0]
    ind_name = ind_info["display_name"]

    # WHEN updating a individual with a valid alignment path
    result = runner.invoke(
        ind_cmd,
        ["--case-id", case_id, "--ind", ind_name, "bam_file", str(bam_path)],
    )

    # THEN the command should run with no errors
    assert result.exit_code == 0
    # THEN assert that the new alignment path was added
    fetched_case = real_populated_database.case_collection.find_one()
    assert fetched_case["individuals"][0]["bam_file"] == str(bam_path)
