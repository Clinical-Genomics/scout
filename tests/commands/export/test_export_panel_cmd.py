# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_export_panel(mock_app):
    """Test the CLI command that exports a gene panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    panel_obj = store.panel_collection.find_one()
    assert panel_obj

    # Test the export panel cli without passing any data
    result = runner.invoke(cli, ["export", "panel"])

    # The CLI command should return an error message then return abort code
    assert result.exit_code == 1
    assert "Please provide at least one gene panel" in result.output

    # Try to pass a non-valid panel name
    result = runner.invoke(cli, ["export", "panel", "unknown_panel"])

    # The CLI command should not return abort code but error message
    assert result.exit_code == 0
    assert "WARNING Panel unknown_panel could not be found" in result.output

    # Try to pass a valid panel name, without a valid version
    result = runner.invoke(cli, ["export", "panel", panel_obj["panel_name"], "--version", 5.0])

    # The CLI command should not return abort code but error message
    assert result.exit_code == 0
    assert "WARNING Panel {} could not be found".format(panel_obj["panel_name"]) in result.output

    # Pass a valid panel name, valid version
    result = runner.invoke(cli, ["export", "panel", panel_obj["panel_name"], "--version", 1.0])

    # The CLI command shoud return gene panel
    assert result.exit_code == 0
    assert "2397\tCRYBB1\t\t\t\t\n9394\tPICK1\t\t\t\t\n" in result.output

    # Pass a valid panel name, valid version, bed file format option
    result = runner.invoke(
        cli, ["export", "panel", panel_obj["panel_name"], "--version", 1.0, "--bed"]
    )

    # The CLI command shoud return gene panel formatted in the expected way
    assert result.exit_code == 0
    assert (
        "22\t26995242\t27014052\t2397\tCRYBB1\n22\t38452318\t38471708\t9394\tPICK1\n"
        in result.output
    )

    # Pass a valid panel name, valid version, bed file format option and genome build GRCh38
    result = runner.invoke(
        cli,
        [
            "export",
            "panel",
            panel_obj["panel_name"],
            "--version",
            1.0,
            "-b",
            "GRCh38",
            "--bed",
        ],
    )

    # The CLI command shoud return gene panel formatted in the expected way
    assert result.exit_code == 0
    assert "##genome_build=GRCh38" in result.output
