# -*- coding: utf-8 -*-

from scout.commands import cli


def test_view_hgnc(mock_app):
    """Testing the CLI that queries for hgnc aliases"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test command without any parameter
    result = runner.invoke(cli, ["view", "hgnc"])
    assert "Please provide a hgnc symbol or hgnc id" in result.output

    # test query by hgnc_symbol
    result = runner.invoke(cli, ["view", "hgnc", "-s", "JUND"])
    assert result.exit_code == 0
    assert "6206\tJUND" in result.output

    # test query by hgnc id
    result = runner.invoke(cli, ["view", "hgnc", "-i", "6206"])
    assert result.exit_code == 0
    assert "6206\tJUND" in result.output

    # test query by hgnc id and build
    result = runner.invoke(cli, ["view", "hgnc", "-i", "6206", "-b", "37"])
    assert result.exit_code == 0
    assert "6206\tJUND" in result.output
