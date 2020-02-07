# -*- coding: utf-8 -*-
import os

from scout.demo import delivery_report_path
from scout.commands import cli


def test_load_delivery_report(mock_app, case_obj):
    """Testing the load delivery report cli command"""

    # Make sure the path to delivery report is a valid path
    assert os.path.isfile(delivery_report_path)

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI function
    result = runner.invoke(
        cli,
        ["load", "delivery-report", case_obj["_id"], delivery_report_path, "-update"],
    )

    assert "saved report to case!" in result.output
    assert result.exit_code == 0
