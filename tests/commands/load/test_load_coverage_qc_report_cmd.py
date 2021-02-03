# -*- coding: utf-8 -*-
import os

from scout.demo import coverage_qc_report_path
from scout.commands import cli


def test_load_coverage_qc_report(mock_app, case_obj):
    """Testing the load coverage qc report cli command"""

    # Make sure the path to delivery report is a valid path
    assert os.path.isfile(coverage_qc_report_path)

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI function
    result = runner.invoke(
        cli,
        ["load", "coverage-qc-report", case_obj["_id"], coverage_qc_report_path, "-u"],
    )

    assert "saved report to case!" in result.output
    assert result.exit_code == 0


def test_invalid_path_load_coverage_qc_report(mock_app, case_obj):
    """Testing the load coverage qc report cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI function
    result = runner.invoke(
        cli,
        ["load", "coverage-qc-report", case_obj["_id"], "invalid-path", "-u"],
    )
    assert "does not exist" in result.output
    assert result.exit_code == 2
