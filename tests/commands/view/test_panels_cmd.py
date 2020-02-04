# -*- coding: utf-8 -*-

from scout.commands import cli


def test_view_panes(mock_app):
    """Test CLI that show all gene panels in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without arguments
    result = runner.invoke(cli, ["view", "panels"])
    assert result.exit_code == 0
    # a panel should be found
    assert "panel1\t1.0\t263" in result.output

    # Provide an non-existing institute argument
    result = runner.invoke(cli, ["view", "panels", "-i", "cust666"])
    # NO panel should be returned by function
    assert "No panels found" in result.output

    # Provide the right institute argument
    result = runner.invoke(cli, ["view", "panels", "-i", "cust000"])
    # a panel should be found
    assert "panel1\t1.0\t263" in result.output
