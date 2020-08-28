# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_update_institute(mock_app):
    """Tests the CLI that updates an institute"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "institute"])
    # it should return error message
    assert "Error: Missing argument" in result.output

    # Test CLI passing institute id that is not in database
    result = runner.invoke(cli, ["update", "institute", "cust666"])
    # it should return error message
    assert "WARNING Institute cust666 does not exist in database" in result.output

    # original institute in database
    institute_obj = store.institute_collection.find_one()
    updates = {
        "coverage_cutoff": 15,
        "frequency_cutoff": 0.05,
        "display_name": "updated_name",
        "sanger_recipients": None,
    }
    # Test CLI to update coverage cutoff
    result = runner.invoke(
        cli, ["update", "institute", "cust000", "-c", updates["coverage_cutoff"]]
    )
    # it should return error message
    assert result.exit_code == 0
    assert "INFO Institute updated" in result.output

    # Test CLI to update display_name
    result = runner.invoke(cli, ["update", "institute", "cust000", "-d", updates["display_name"]])
    # it should return error message
    assert result.exit_code == 0
    assert "INFO Institute updated" in result.output

    # Test CLI to update frequency_cutoff
    result = runner.invoke(
        cli, ["update", "institute", "cust000", "-f", updates["frequency_cutoff"]]
    )
    # it should return error message
    assert result.exit_code == 0
    assert "INFO Institute updated" in result.output

    # Test CLI to remove a sanger recipient
    result = runner.invoke(
        cli,
        ["update", "institute", "cust000", "-r", institute_obj["sanger_recipients"][0]],
    )
    # it should return error message
    assert result.exit_code == 0
    assert "INFO Institute updated" in result.output

    # check that updates were really performed on database:
    updated_institute = store.institute_collection.find_one()
    for key in updates.keys():
        assert institute_obj[key] != updated_institute[key]

    # Test CLI to update sanger recipients
    result = runner.invoke(
        cli,
        ["update", "institute", "cust000", "-s", institute_obj["sanger_recipients"][0]],
    )
    # it should return error message
    assert result.exit_code == 0
    assert "INFO Institute updated" in result.output

    # make sure that recipient has been introduced
    updated_institute = store.institute_collection.find_one()
    # updated sanger recipients should be equal but in reversed order
    # to recipients in original institute object
    assert updated_institute["sanger_recipients"] == institute_obj["sanger_recipients"][::-1]
