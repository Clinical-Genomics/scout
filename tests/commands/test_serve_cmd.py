# -*- coding: utf-8 -*-

from scout.commands import cli


def test_serve(mock_app):
    """Test the CLI command that runs the app"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command:
    result = runner.invoke(cli, ["serve", "--test"])
    assert result.exit_code == 0
    assert "Connection could be established" in result.output
