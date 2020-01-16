# -*- coding: utf-8 -*-

from scout.commands import cli

from scout.server.extensions import store


def test_view_index(mock_app):
    """Test CLI that shows all indexes in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["view", "index"])
    assert result.exit_code == 0
    # no term shold be returned
    assert "event\tvariant_id" in result.output

    # Test CLI base with argument collection name
    result = runner.invoke(cli, ["view", "index", "-n", "variant"])
    assert result.exit_code == 0
    # this time indexes in event collection should not be found
    assert "event\tvariant_id" not in result.output
    # but indexes of variant collection are shown
    assert "variant\tsanger" in result.output
