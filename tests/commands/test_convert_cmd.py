"""Test the CLI command that converts a gene panel with hgnc symbols to a new one with hgnc ids"""
# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.demo import panel_path


def test_convert_missing_args(mock_app):
    """test the command with missing args"""

    runner = mock_app.test_cli_runner()

    # Test CLI without providing panel file
    result = runner.invoke(cli, ["convert"])

    # It should return error message
    assert "Missing argument" in result.output


def test_convert_wrong_path(mock_app):
    """test the command with missing args"""
    runner = mock_app.test_cli_runner()

    # Provide a non-valid path to a panel file
    result = runner.invoke(cli, ["convert", "wrong/path/to/file"])
    assert result.exit_code != 0
    assert "Could not open file: wrong/path/to/file:" in result.output
    runner = mock_app.test_cli_runner()


def test_convert_panel(mock_app):
    """test the command with missing args"""
    runner = mock_app.test_cli_runner()

    # Provide a valid path to a panel file
    result = runner.invoke(cli, ["convert", panel_path])
    # genes should be converted as expected
    assert result.exit_code == 0
    assert "2397\tCRYBB1\t\t\t\t\t\n9394\tPICK1" in result.output
