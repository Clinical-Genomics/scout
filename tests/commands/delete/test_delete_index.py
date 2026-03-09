from scout.commands import cli
from scout.server.extensions import store


def test_delete_index(empty_mock_app):
    "Test the CLI command that will drop indexes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner
    ## GIVEN an adapter with indexes
    store.load_indexes()
    indexes = list(store.case_collection.list_indexes())
    assert len(indexes) > 1

    ## WHEN removing all indexes using the CLI
    result = runner.invoke(cli, ["delete", "index"])

    ## THEN assert that the function should not exit with error
    assert result.exit_code == 0
    assert "All indexes deleted" in result.output

    ## THEN assert all indexes should be gone
    indexes = list(store.case_collection.list_indexes())
    assert len(indexes) == 1  # _id index is the only index left
