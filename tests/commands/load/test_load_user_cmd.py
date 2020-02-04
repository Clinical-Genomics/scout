# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_load_user(mock_app, user_obj):
    """Testing the load user cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # One user is preloaded into populated database
    assert sum(1 for i in store.user_collection.find()) == 1

    # remove it
    store.user_collection.find_one_and_delete({"_id": user_obj["_id"]})
    assert store.user_collection.find_one() is None

    # and re-load it using the CLI command:
    result = runner.invoke(
        cli,
        [
            "load",
            "user",
            "-i",
            user_obj["institutes"][0],
            "-u",
            user_obj["name"],
            "-m",
            user_obj["email"],
            "--admin",
        ],
    )

    # CLI command should be exit with no errors
    assert result.exit_code == 0

    # And the user should be in database:
    assert sum(1 for i in store.user_collection.find({"_id": user_obj["email"]})) == 1
