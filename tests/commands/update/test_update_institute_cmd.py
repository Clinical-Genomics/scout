# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_update_institute_missing_arg(mock_app):
    """Test the command line to update an institute when no argument is provided."""
    # GIVEN a CLI mock runner
    runner = mock_app.test_cli_runner()

    # WHEN testing the CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "institute"])
    # THEN it should return error message
    assert "Error: Missing argument" in result.output


def test_update_institute_non_existing(mock_app):
    """Test the command line to update an institute when the provided institute doesn't exist.."""
    # GIVEN a CLI mock runner
    runner = mock_app.test_cli_runner()
    # WHEN the passed institute doesn't exist in the database
    result = runner.invoke(cli, ["update", "institute", "cust666"])
    # THEN it should return error message
    assert "WARNING Institute cust666 does not exist in database" in result.output


def test_update_institute_coverage_cutoff(mock_app):
    """Test the command line to update the coverage cutoff of an institute."""

    coverage_cutoff = 15
    # GIVEN a CLI mock runner
    runner = mock_app.test_cli_runner()

    # WHEN updating the coverage cutoff via CLI
    result = runner.invoke(cli, ["update", "institute", "cust000", "-c", coverage_cutoff])
    # THEN it should NOT return error
    assert result.exit_code == 0

    # AND the institute should have the expected coverage cutoff
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["coverage_cutoff"] == coverage_cutoff


def test_update_institute_frequency_cutoff(mock_app):
    """Test the command line to update the frequency cutoff of an institute."""

    frequency_cutoff = 0.05
    # GIVEN a CLI mock runner
    runner = mock_app.test_cli_runner()

    # GIVEN an existing institute in a database
    institute_obj = store.institute_collection.find_one()
    # WITH a frequency cutoff
    old_cutoff = institute_obj["frequency_cutoff"]

    # WHEN updating the frequency cutoff via CLI
    result = runner.invoke(cli, ["update", "institute", "cust000", "-f", frequency_cutoff])
    # THEN it should NOT return error
    assert result.exit_code == 0

    # AND the institute should have the new frequency coverage cutoff
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["frequency_cutoff"] > old_cutoff


def test_update_institute_display_name(mock_app):
    """Test the command line to update the display name of an institute."""
    updated_name = "updated_name"

    # GIVEN a CLI mock runner
    runner = mock_app.test_cli_runner()

    # WHEN updating the frequency cutoff via CLI
    result = runner.invoke(cli, ["update", "institute", "cust000", "-d", updated_name])
    # THEN it should NOT return error
    assert result.exit_code == 0

    # AND the institute should be updated
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["display_name"] == updated_name


def test_update_institute_sanger_recipients(mock_app):
    """Test the command line to update Sanger recipients of an institute."""

    # GIVEN a CLI mock runner
    runner = mock_app.test_cli_runner()

    # GIVEN an existing institute in a database
    institute_obj = store.institute_collection.find_one()
    # WITH Sanger recipients
    old_recipients = institute_obj["sanger_recipients"]
    assert len(old_recipients) > 1

    # WHEN removing a recipient using the command line
    # Test CLI to remove a sanger recipient
    result = runner.invoke(
        cli,
        ["update", "institute", "cust000", "-r", old_recipients[0]],
    )
    # THEN the command should be successful
    assert result.exit_code == 0
    # AND the institute should be updated
    updated_institute = store.institute_collection.find_one()
    updated_recipients = updated_institute["sanger_recipients"]
    assert len(old_recipients) > len(updated_recipients)

    # WHEN when all recipients are gone
    runner.invoke(
        cli,
        ["update", "institute", "cust000", "-r", updated_recipients[0]],
    )
    updated_institute = store.institute_collection.find_one()
    # THEN the sanger_recipients key should also be gone
    assert "sanger_recipients" not in updated_institute

    # WHEN a new recipient is added to the institute
    result = runner.invoke(
        cli,
        ["update", "institute", "cust000", "-s", updated_recipients[0]],
    )
    # THEN the command should be successful
    assert result.exit_code == 0
    # AND the recipient should be found in the institute
    updated_institute = store.institute_collection.find_one()
    assert updated_institute["sanger_recipients"] == updated_recipients
