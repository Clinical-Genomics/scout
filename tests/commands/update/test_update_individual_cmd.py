"""Tests for update individual command"""

from click.testing import CliRunner

from scout.commands.update.individual import individual as ind_cmd

# from scout.server.extensions import store


def test_update_individual_no_args():
    """Tests the CLI that updates a individual"""

    # GIVEN a CLI object
    runner = CliRunner()

    # WHEN updating a individual without any args
    result = runner.invoke(ind_cmd)

    # THEN assert it fails since its missing mandatory arguments
    assert result.exit_code == 2


def test_update_individual(empty_mock_app):
    """Tests the CLI that updates a individual"""

    # GIVEN a CLI object
    runner = empty_mock_app.test_cli_runner()

    # WHEN updating a individual without case and ind
    result = runner.invoke(ind_cmd, ["--case-id", "acase", "--ind-id", "anind"])

    # THEN assert it exits without problems
    assert result.exit_code == 0


def test_update_individual_existing(empty_mock_app, real_adapter):
    """Tests the CLI that updates a individual"""

    # GIVEN a CLI object
    runner = empty_mock_app.test_cli_runner()
    # GIVEN a database with a case_obj
    case_id = "acase"
    ind_id = "anind"
    case_obj = {"case_id": case_id, "individuals": [{"individual_id": ind_id}]}
    real_adapter.case_collection.insert_one(case_obj)

    # WHEN updating a individual without case and ind
    result = runner.invoke(ind_cmd, ["--case-id", case_id, "--ind-id", ind_id])

    # THEN assert it exits without problems since nothing happened
    assert result.exit_code == 0


def test_update_alignment_path(mock_app, real_populated_database, bam_path):
    """Tests the CLI that updates a individual"""

    # GIVEN a CLI object
    runner = mock_app.test_cli_runner()
    # GIVEN a database with a case_obj
    existing_case = real_populated_database.case_collection.find_one()
    case_id = existing_case["_id"]
    ind_info = existing_case["individuals"][0]
    ind_id = ind_info["individual_id"]

    # WHEN updating a individual without case and ind
    result = runner.invoke(
        ind_cmd,
        ["--case-id", case_id, "--ind-id", ind_id, "--alignment-path", str(bam_path)],
    )

    # THEN assert it exits without problems
    assert result.exit_code == 0
    # THEN assert that the new alignment path was added
    fetched_case = real_populated_database.case_collection.find_one()
    assert fetched_case["individuals"][0]["bam_file"] == str(bam_path.resolve())
