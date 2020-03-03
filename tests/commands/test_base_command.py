import pytest

from click.testing import CliRunner
from scout.commands import cli
from scout import __version__

# Sanity check for cli
def test_base_cmd():

    # Create a test CLI runner
    runner = CliRunner()
    assert runner

    # test the CLI base, no arguments provided
    result = runner.invoke(cli)
    assert result.exit_code == 0
    # debug message should be printed
    assert "Debug logging enabled." in result.output

    # test the cli with a different loglevel that DEBUG
    result = runner.invoke(cli, ["--loglevel", "WARNING"])
    assert result.exit_code == 0
    # debug message should NOT be printed
    assert "Debug logging enabled." not in result.output

    # test the cli with -v (version) option
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output

    # test the cli with --demo option
    result = runner.invoke(cli, ["--demo"])
    assert result.exit_code == 0
    assert "connecting to database:" in result.output and "scout-demo" in result.output
