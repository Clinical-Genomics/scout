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
        "This will delete and rebuild indexes(if not --update) for the given collections (or the whole database). Are you sure?"
        in result.output
    )

    # Provide confirm command to CLI (say yes)
    result = runner.invoke(cli, ["index", "-c", "hgnc_gene"], input="y")
    assert result.exit_code == 0
    assert "INFO creating indexes" in result.output

    # Provide confirm command and update option
    result = runner.invoke(cli, ["index", "--update", "-c", "hgnc_gene"], input="y")
    assert result.exit_code == 0
    assert "INFO All indexes in place" in result.output
