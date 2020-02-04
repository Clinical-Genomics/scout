# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_view_cases(mock_app):
    """Tests the CLI that displays cases from the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["view", "cases"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # Test CLI base providing an institute not in database
    result = runner.invoke(cli, ["view", "cases", "-i", "cust666"])
    assert result.exit_code == 0
    # test case should NOT be returned
    assert "No cases could be found" in result.output

    # Test CLI base providing an existing institute
    result = runner.invoke(cli, ["view", "cases", "-i", "cust000"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # Test CLI base providing display name
    result = runner.invoke(cli, ["view", "cases", "-d", "643594"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # Test CLI base providing case _id
    result = runner.invoke(cli, ["view", "cases", "-c", "internal_id"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # load research variants for this case:
    result = runner.invoke(cli, ["load", "variants", "internal_id", "--snv"])
    assert result.exit_code == 0
    n_vars = sum(1 for i in store.variant_collection.find())
    assert n_vars > 0

    # Test CLI with --nr-variants flag
    result = runner.invoke(cli, ["view", "cases", "-c", "internal_id", "--nr-variants"])
    assert result.exit_code == 0
    # number of variants should be shown in output
    assert str(n_vars) in result.output

    # Test CLI with --variants-treshold param
    result = runner.invoke(cli, ["view", "cases", "--variants-treshold", n_vars])
    assert result.exit_code == 0
    # number of variants should be shown in output
    assert str(n_vars) in result.output

    # Test CLI with --variants-treshold param
    result = runner.invoke(cli, ["view", "cases", "--variants-treshold", n_vars + 1])
    assert result.exit_code == 0
    # number of variants should be shown in output
    assert "Displaying number of variants for each case" in result.output
