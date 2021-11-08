# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.demo.resources import reduced_resources_path


def test_update_genes_from_downloaded_resources(mock_app):
    """Tests the CLI that updates genes in database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, provide non-valid API key
    result = runner.invoke(cli, ["update", "genes", "-f", reduced_resources_path])
    assert result.exit_code == 0
