# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_load_exons(mock_app, exons_file):
    """Test the CLI command that loads a gene panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI by passing the reduced exons file
    result = runner.invoke(cli, ["load", "exons", "-b", "37", "-e", exons_file])
    assert result.exit_code == 0
