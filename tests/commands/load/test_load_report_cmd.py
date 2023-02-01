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
                "load",
                "report",
                "-t",
                report_types,
                case_id,
                report_path,
            ],
        )

        # THEN the command should be succesful
        assert result.exit_code == 0

        # And the report should have been loaded
        updated_case = store.case_collection.find_one()
        assert updated_case[CUSTOM_CASE_REPORTS[report_types]["key_name"]] == report_path


def test_load_gene_fusion_report_research(mock_app):
    """Test command line function that load a gene fusion research report for an existing case"""
    # GIVEN a database with an existing case
    case_obj = store.case_collection.find_one()
    case_id = case_obj["_id"]

    # GIVEN that this case has no gene fusion research report
    assert case_obj.get("gene_fusion_report_research") is None

    runner = mock_app.test_cli_runner()

    # WHEN the update_gene_fusion command is executed provifing a new gene fusion research report
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
        research_gene_fusion_report_path = os.path.dirname(tf.name)
        result = runner.invoke(
            cli,
            [
                "load",
                "gene-fusion-report",
                case_id,
                research_gene_fusion_report_path,
                "--research",
            ],
        )

        # THEN the command should be succesful
        assert result.exit_code == 0

        # And the gene fusion research report should have been updated
        updated_case = store.case_collection.find_one()
        assert updated_case["gene_fusion_report_research"]


def test_load_gene_fusion_report_update(mock_app):
    """Test command line function that updated the gene fusion report for an existing case"""
    # GIVEN a database with an existing case
    case_obj = store.case_collection.find_one()

    # GIVEN that this case has an old gene fusion report
    old_report = case_obj.get("gene_fusion_report")
    assert old_report

    case_id = case_obj["_id"]
    runner = mock_app.test_cli_runner()

    # WHEN the update_gene_fusion command is executed provifing a new gene fusion report
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
        new_report_path = os.path.dirname(tf.name)
        result = runner.invoke(
            cli, ["load", "gene-fusion-report", case_id, new_report_path, "--update"]
        )

        # THEN the command should be succesful
        assert result.exit_code == 0

        # And the gene fusion report should have been updated
        updated_case = store.case_collection.find_one()
        assert updated_case["gene_fusion_report"] != old_report
