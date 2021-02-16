# -*- coding: utf-8 -*-
import os
import tempfile

from scout.commands import cli
from scout.server.extensions import store


def test_load_gene_fusion_report(mock_app):
    """Test command line function that updated the gene fusion report for an existing case"""
    # GIVEN a database with an existing case
    case_obj = store.case_collection.find_one()

    # GIVEN that this case has an old gene fusion report
    old_report = case_obj.get("gene_fusion_report")

    case_id = case_obj["_id"]
    runner = mock_app.test_cli_runner()

    # WHEN the update_gene_fusion command is executed provifing a new gene fusion report
    with tempfile.NamedTemporaryFile(suffix=".tsv") as tf:

        new_report_path = os.path.dirname(tf.name)
        result = runner.invoke(
            cli, ["load", "gene-fusion-report", case_id, new_report_path, "--update"]
        )

        # THEN the command should be succesful
        assert result.exit_code == 0

        # And the gene fusion report should have been updated
        updated_case = store.case_collection.find_one()
        assert updated_case["gene_fusion_report"] != old_report
