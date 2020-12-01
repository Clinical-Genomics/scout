# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_export_mt_report(mock_app, case_obj):
    """Test the CLI command that exports the MT variants"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Thy the CLI without parameters
    result = runner.invoke(cli, ["export", "mt_report"])
    # it should return error
    assert "Missing option" in result.output

    # Test the CLI providing case_id
    result = runner.invoke(cli, ["export", "mt_report", "--case_id", case_obj["_id"], "--test"])
    # there are no variants in database so you should get an error message
    assert "There are no MT variants associated to case" in result.output

    # load case variants into database
    assert store.variant_collection.find_one() is None
    result = runner.invoke(cli, ["load", "variants", case_obj["_id"], "--snv"])
    assert "INFO Updating variant_rank done" in result.output
    assert sum(1 for i in store.variant_collection.find({"chromosome": "MT"})) > 0

    # Test the CLI providing case_id
    result = runner.invoke(cli, ["export", "mt_report", "--case_id", case_obj["_id"], "--test"])
    assert result.exit_code == 0
    # This time it should return a message saying thate Excel files can be written to outfolder
    assert "INFO Number of excel files that can be written to folder" in result.output
