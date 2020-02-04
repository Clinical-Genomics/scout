# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_index(mock_app):
    """Test the CLI that creates indexes in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test the command that updates the indexes without arguments
    result = runner.invoke(cli, ["index"])
    # It should print confirm message
    assert (
        "This will delete and rebuild all indexes(if not --update). Are you sure? [y/N]"
        in result.output
    )

    # Provide confirm command to CLI (say yes)
    result = runner.invoke(cli, ["index"], input="y")
    assert result.exit_code == 0
    assert "INFO creating indexes" in result.output

    # Provide confirm command and update option
    result = runner.invoke(cli, ["index", "--update"], input="y")
    assert result.exit_code == 0
    assert "INFO All indexes in place" in result.output
