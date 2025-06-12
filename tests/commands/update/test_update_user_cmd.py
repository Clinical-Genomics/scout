# -*- coding: utf-8 -*-

import pytest

from scout.commands import cli
from scout.commands.update.user import USER_ROLES
from scout.server.extensions import store


def test_update_user_institute(mock_app, user_obj):
    """Test the command line to add and remove institutes associated to a user."""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result = runner.invoke(cli, ["update", "user"])
    # it should return error message
    assert "Missing option" in result.output

    # Test CLI with wrong user
    result = runner.invoke(cli, ["update", "user", "-u", "unknown_user_id"])
    # it should return error message
    assert "User unknown_user_id could not be found" in result.output

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


@pytest.mark.parametrize("role", USER_ROLES)
def test_update_user_role(role, mock_app, user_obj):
    """Test the command line to add and remove a generic role for a user."""
    runner = mock_app.test_cli_runner()

    # GIVEN a non-admin user in the database
    result = runner.invoke(cli, ["update", "user", "-u", user_obj["_id"], "--remove-admin"])
    assert "INFO Updating user {}".format(user_obj["_id"]) in result.output
    updated_user = store.user_collection.find_one()
    assert "admin" not in updated_user["roles"]

    # THEN it should be possible to add/remove any role to it
    runner.invoke(cli, ["update", "user", "-u", user_obj["_id"], "-r", role])
    updated_user = store.user_collection.find_one()
    assert role in updated_user["roles"]

    runner.invoke(cli, ["update", "user", "-u", user_obj["_id"], "--remove-role", role])
    updated_user = store.user_collection.find_one()
    assert role not in updated_user["roles"]
