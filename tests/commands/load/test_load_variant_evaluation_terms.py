# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.resources import default_evaluations_file_path


def test_load_default_terms(mock_app, adapter):
    """Test loading default variant evaluation terms into database"""

    # GIVEN that the command for loading the default evaluation terms into database is executed
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["load", "evaluation-terms", "default"], input="y")

    # THEN assert that the program exits without problems
    assert result.exit_code == 0


def test_load_custom_terms(mock_app, adapter):
    """Test loading custom variant evaluation terms contained in a json file into database"""

    # GIVEN that the command for loading custom evaluations from file is executed
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        ["load", "evaluation-terms", "custom", "--file", default_evaluations_file_path],
        input="y",
    )

    # THEN assert that the program exits without problems
    assert result.exit_code == 0
