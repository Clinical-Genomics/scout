# -*- coding: utf-8 -*-
import os
import tempfile

from scout.commands import cli
from scout.server.extensions import store


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
            ["load", "gene-fusion-report", case_id, research_gene_fusion_report_path, "--research"],
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
