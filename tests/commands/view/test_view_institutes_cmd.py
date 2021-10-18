# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_view_institutes(mock_app, institute_obj):
    """Test CLI that shows all institutes in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without arguments
    result = runner.invoke(cli, ["view", "institutes"])
    assert result.exit_code == 0
    # an institute should be found
    assert (
        "\t".join(
            [
                institute_obj["internal_id"],
                institute_obj["internal_id"],
                institute_obj["display_name"],
            ]
        )
        in result.output
    )

    # Test CLI with --json flag
    result = runner.invoke(cli, ["view", "institutes", "--json"])
    assert result.exit_code == 0
    # Make sure right formatting is returned
    assert "'internal_id': 'cust000'" in result.output

    # Test the app by providing an institute that does not exist in database
    result = runner.invoke(cli, ["view", "institutes", "-i", "cust666"])
    # istitute is not found
    assert "Institute cust666 does not exist" in result.output

    # remove institute from database
    store.institute_collection.find_one_and_delete({"_id": institute_obj["internal_id"]})
    assert sum(1 for i in store.institute_collection.find()) == 0

    # Test cli again with no institutes in database
    result = runner.invoke(cli, ["view", "institutes"])
    # No institute should be found
    assert "No institutes found" in result.output
