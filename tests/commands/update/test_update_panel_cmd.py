# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store

from scout.utils.date import get_date


def test_update_panel(mock_app):
    """Tests the CLI that updates a panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "panel"])
    # it should return error message
    assert 'Missing option "--panel"' in result.output

    # Test CLI providing unknown panel
    result = runner.invoke(cli, ["update", "panel", "-p", "unknown_panel"])
    assert "could not be found" in result.output

    # Test updating date providing a valid panel
    result = runner.invoke(
        cli, ["update", "panel", "-p", "panel1", "--update-date", "2019-03-29"]
    )
    assert "panels.$.updated_at" in result.output

    # update panel version specifying original panel version
    result = runner.invoke(
        cli,
        ["update", "panel", "-p", "panel1", "--version", 1.0, "--update-version", 2.0],
    )
    assert "$set': {'panels.$.version': 2.0" in result.output
