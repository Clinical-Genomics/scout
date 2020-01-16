# -*- coding: utf-8 -*-

from scout.commands import cli


def test_view_intervals(mock_app):
    """Test CLI that show all coding intervals in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without arguments
    result = runner.invoke(cli, ["view", "intervals"])
    assert result.exit_code == 0
    # and command should work
    assert "Longest interval" in result.output

    # Test CLI providing a different build
    result = runner.invoke(cli, ["view", "intervals", "-b", "38"])
    # command should trigger adapter function
    assert result.exit_code == 0
    # but no data is returned
    assert "No genes in database with build 38" in result.output

    # Test CLI providing an existing build
    result = runner.invoke(cli, ["view", "intervals", "-b", "37"])
    assert result.exit_code == 0
    # and command should return data
    assert "Longest interval" in result.output
