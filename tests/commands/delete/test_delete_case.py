from scout.commands import cli
from scout.server.extensions import store


def test_delete_case_no_specs(empty_mock_app, case_obj):
    "Test the CLI command that will delete a case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    assert store.case_collection.find_one() is None
    ## GIVEN a adapter with a case
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one()
    ## WHEN deleting case without specifying anything
    result = runner.invoke(cli, ["delete", "case"])
    ## THEN assert corrects information is communicated
    assert "Please specify what case to delete" in result.output
    ## THEN assert the cli exits with error
    assert result.exit_code == 1
    ## THEN assert there is a case left
    assert store.case_collection.find_one()


def test_delete_case_wrong_id(empty_mock_app, case_obj):
    "Test the CLI command that will delete a case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN a adapter with a case
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one()

    ## WHEN deleting case with non exosting id
    result = runner.invoke(cli, ["delete", "case", "-i", case_obj["owner"], "-c", "unknown_id"])

    ## THEN assert the correct information is communicated
    assert "Couldn't find any case in database matching the provided parameters" in result.output
    ## THEN assert the cli exits with error
    assert result.exit_code == 1
    ## THEN assert there is a case left
    assert store.case_collection.find_one()


def test_delete_case(empty_mock_app, case_obj):
    "Test the CLI command that will delete a case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN a adapter with a case
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one()

    ## WHEN deleting the case
    result = runner.invoke(cli, ["delete", "case", "-c", case_obj["_id"]])
    ## THEN assert it exits without problems
    assert result.exit_code == 0

    ## THEN assert the case is gone
    assert store.case_collection.find_one() is None


def test_delete_case_no_institute(empty_mock_app, case_obj):
    "Test the CLI command that will delete a case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN a adapter with a case
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one()

    ## WHEN providing the right display_name but not institute
    result = runner.invoke(cli, ["delete", "case", "-d", case_obj["display_name"]])
    ## THEN assert it exots with error
    assert result.exit_code == 1
    ## THEN assert the correct information is communicated
    assert "Please specify the owner of the case that should be deleted" in result.output

    # Provide right display_name and right institute
    result = runner.invoke(
        cli, ["delete", "case", "-d", case_obj["display_name"], "-i", case_obj["owner"]]
    )

    # and the case should have been removed again
    assert result.exit_code == 0
    assert sum(1 for _ in store.case_collection.find()) == 0


def test_delete_case_correct_institute(empty_mock_app, case_obj):
    "Test the CLI command that will delete a case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN a adapter with a case
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one()

    ## WHEN providing the right display_name and institute
    result = runner.invoke(
        cli, ["delete", "case", "-d", case_obj["display_name"], "-i", case_obj["owner"]]
    )

    ## THEN assert case should have been removed
    assert store.case_collection.find_one() is None
    ## THEN assert the CLI exits without problems
    assert result.exit_code == 0
