# -*- coding: utf-8 -*-
import os
from copy import deepcopy

import pytest

from scout.commands import cli
from scout.demo import delivery_report_path


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


def test_exception_load_delivery_report(mock_app, case_obj):
    """Testing the load delivery report cli command for exception"""

    test_case_obj = deepcopy(case_obj)
    test_case_obj["_id"] = "some_very_wrong_and_nonexisting_case"

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI function
    with pytest.raises(Exception) as raised_exception:
        result = runner.invoke(
            cli,
            ["load", "delivery-report", test_case_obj["_id"], coverage_qc_report_path, "-u"],
        )
        assert result.exit_code == 2
