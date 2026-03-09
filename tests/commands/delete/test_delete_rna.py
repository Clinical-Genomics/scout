from scout.commands import cli
from scout.commands.delete.rna import CASE_RNA_KEYS
from scout.server.extensions import store


def test_delete_rna(empty_mock_app, case_obj):
    """Test the command that is removing RNA data from a case."""

    # GIVEN a case with RNA data
    assert any(key in case_obj and case_obj[key] for key in CASE_RNA_KEYS)
    store.case_collection.insert_one(case_obj)

    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    # WHEN data is erased using the cli
    result = runner.invoke(cli, ["delete", "rna", "-c", case_obj["_id"]], input="y\n")

    # THEN RNA data is removed from the case
    assert result.exit_code == 0
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert all(not updated_case.get(key) for key in CASE_RNA_KEYS)
