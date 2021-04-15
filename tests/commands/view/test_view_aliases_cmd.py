# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_view_aliases(mock_app):
    """Test CLI that shows all alias symbols and how they map to ids"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI with no parameters
    result = runner.invoke(cli, ["view", "aliases"])
    # command should work and genes are found
    assert result.exit_code == 0
    assert "SRY\t11311\t11311" in result.output

    # Test CLI providing a gene symbol that does not exist in database
    result = runner.invoke(cli, ["view", "aliases", "-s", "BAH"])
    assert result.exit_code == 0
    assert "No gene found for build 37" in result.output

    # Test CLI providing a gene symbol that exists
    result = runner.invoke(cli, ["view", "aliases", "-s", "BCR"])
    assert result.exit_code == 0
    # command should work and genes are found
    assert "BCR" in result.output

    # Test CLI providing a gene symbol that exists and buil param
    result = runner.invoke(cli, ["view", "aliases", "-s", "BCR", "-b", "38"])
    assert result.exit_code == 0
    # command should work but there are no genes with build 38
    assert "No gene found for build 38" in result.output
