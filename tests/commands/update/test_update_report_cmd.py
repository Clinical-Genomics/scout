# -*- coding: utf-8 -*-
import os
import tempfile

import pytest

from scout.commands import cli
from scout.constants import CUSTOM_CASE_REPORTS
from scout.server.extensions import store


@pytest.mark.parametrize("report_types", list(CUSTOM_CASE_REPORTS.keys()))
def test_load_case_report(mock_app, report_types):
    """Test the command to load/update one of the available reports for a case"""
    # GIVEN a database with an existing case
    case_obj = store.case_collection.find_one()
    case_id = case_obj["_id"]

    runner = mock_app.test_cli_runner()

    with tempfile.NamedTemporaryFile(suffix=".html") as tf:
        # WHEN the "scout load report <report-type> command is executed
        report_path = os.path.dirname(tf.name)
        result = runner.invoke(
            cli,
            [
                "update",
                "report",
                "-t",
                report_types,
                case_id,
                report_path,
            ],
        )

        # THEN the command should be successful
        assert result.exit_code == 0

        # And the report should have been loaded
        updated_case = store.case_collection.find_one()
        assert updated_case[CUSTOM_CASE_REPORTS[report_types]["key_name"]] == report_path

    # WHEN executing the command to delete the same report
    result = runner.invoke(
        cli,
        [
            "update",
            "report",
            "-t",
            report_types,
            "--delete",
            case_id,
        ],
    )

    # THEN the command should be successful
    assert result.exit_code == 0

    # THEN the report should have been deleted again
    updated_case = store.case_collection.find_one()
    assert CUSTOM_CASE_REPORTS[report_types]["key_name"] not in updated_case
