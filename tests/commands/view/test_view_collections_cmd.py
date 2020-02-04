# -*- coding: utf-8 -*-

from scout.commands import cli

from scout.server.extensions import store


def test_view_diseases(mock_app):
    """Test CLI that shows all collections in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI
    result = runner.invoke(cli, ["view", "collections"])
    assert result.exit_code == 0
    for collection in ["gene_panel", "case", "institute", "exon", "event", "variant"]:
        assert collection in result.output
