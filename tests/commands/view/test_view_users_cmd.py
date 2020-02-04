# -*- coding: utf-8 -*-

from scout.commands import cli


def test_view_users(mock_app):
    """Test CLI that show all users in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without arguments
    result = runner.invoke(cli, ["view", "users"])
    assert result.exit_code == 0
    # a user should be found
    assert "John Doe\tjohn@doe.com\tadmin\tcust000" in result.output
