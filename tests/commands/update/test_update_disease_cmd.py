# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.demo.resources import reduced_resources_path


def test_update_diseases(mock_app):
    """Tests the CLI that updates disease terms in database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(
        cli,
        ["update", "diseases", "--downloads-folder", reduced_resources_path],
    )
    # command should run without errors
    assert result.exit_code == 0
