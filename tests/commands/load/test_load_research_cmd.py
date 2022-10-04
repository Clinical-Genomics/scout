# -*- coding: utf-8 -*-

from scout.commands import cli


def test_load_research(mock_app, case_obj):
    """Testing the load research cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test command without case_id:
    result = runner.invoke(cli, ["load", "research"])
    assert result.exit_code == 0

    # Test command providing a case_id:
    result = runner.invoke(cli, ["load", "research", "-c", case_obj["_id"]])
    assert result.exit_code == 0

    # Test command providing case_id, institute and force flag:
    result = runner.invoke(
        cli, ["load", "research", "-c", case_obj["_id"], "-i", case_obj["owner"], "-f"]
    )
    assert result.exit_code == 0
