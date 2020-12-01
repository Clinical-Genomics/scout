# -*- coding: utf-8 -*-
import os

from scout.demo import cnv_report_path
from scout.commands import cli


def test_load_cnv_report(mock_app, case_obj):
    """Testing the load delivery report cli command"""

    # Make sure the path to delivery report is a valid path
    assert os.path.isfile(cnv_report_path)

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI function
    result = runner.invoke(
        cli,
        ["load", "cnv-report", case_obj["_id"], cnv_report_path, "-u"],
    )

    assert "saved report to case!" in result.output
    assert result.exit_code == 0


def test_invalid_path_load_cnv_report(mock_app, case_obj):
    """Testing the load delivery report cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI function
    result = runner.invoke(
        cli,
        ["load", "cnv-report", case_obj["_id"], "invalid-path", "-u"],
    )

    assert "Path 'invalid-path' does not exist." in result.output
    assert result.exit_code == 2
