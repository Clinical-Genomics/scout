from scout.commands import cli
from scout.server.extensions import store


def test_delete_panel_non_existing(empty_mock_app, testpanel_obj):
    "Test the CLI command that deletes a gene panel"
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN database with a gene panel
    store.panel_collection.insert_one(testpanel_obj)

    ## WHEN fetching giving a wrong version
    result = runner.invoke(
        cli,
        [
            "delete",
            "panel",
            "--panel-id",
            testpanel_obj["panel_name"],
            "-v",
            5.0,  # db_panel version is 1.0
        ],
    )

    ## THEN assert no panel was found
    assert "No panels found" in result.output


def test_delete_panel(empty_mock_app, testpanel_obj):
    "Test the CLI command that deletes a gene panel"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN database with a gene panel
    store.panel_collection.insert_one(testpanel_obj)

    # Test the CLI by using panel name without version
    result = runner.invoke(cli, ["delete", "panel", "--panel-id", testpanel_obj["panel_name"]])

    # Panel should be correctly removed from database
    assert "WARNING Deleting panel {}".format(testpanel_obj["panel_name"]) in result.output

    # And no panels ahould be available in database
    assert sum(1 for _ in store.panel_collection.find()) == 0
