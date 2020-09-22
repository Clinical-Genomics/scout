# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_update_user(mock_app, user_obj):
    """Tests the CLI that updates a user"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "user"])
    # it should return error message
    assert "Missing option" in result.output

    # Test CLI with wrong user
    result = runner.invoke(cli, ["update", "user", "-u", "unknown_user_id"])
    # it should return error message
    assert "User unknown_user_id could not be foun" in result.output

    # Test CLI with right user, update user role
    # remove admin role first:
    result = runner.invoke(cli, ["update", "user", "-u", user_obj["_id"], "--remove-admin"])
    assert "INFO Updating user {}".format(user_obj["_id"]) in result.output
    updated_user = store.user_collection.find_one()
    assert "admin" not in updated_user["roles"]

    # Test CLI to add admin role to user
    result = runner.invoke(cli, ["update", "user", "-u", user_obj["_id"], "-r", "admin"])
    assert "INFO Updating user {}".format(user_obj["_id"]) in result.output
    updated_user = store.user_collection.find_one()
    assert "admin" in updated_user["roles"]

    # Test CLI to remove an institute from a user
    result = runner.invoke(
        cli, ["update", "user", "-u", user_obj["_id"], "--remove-institute", "cust000"]
    )
    assert "INFO Updating user {}".format(user_obj["_id"]) in result.output
    updated_user = store.user_collection.find_one()
    assert "cust000" not in updated_user["institutes"]

    # Test CLI to add a institute to user's institutes
    result = runner.invoke(cli, ["update", "user", "-u", user_obj["_id"], "-i", "cust000"])
    assert "INFO Updating user {}".format(user_obj["_id"]) in result.output
    updated_user = store.user_collection.find_one()
    assert "cust000" in updated_user["institutes"]
