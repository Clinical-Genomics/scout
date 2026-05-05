from scout.commands import cli
from scout.demo import rank_score_path, sv_rank_score_path
from scout.server.extensions import store


def test_delete_rank_model(empty_mock_app):
    """Test the delete_rank_model command"""

    runner = empty_mock_app.test_cli_runner()
    assert runner

    ## GIVEN an empty db

    ## WHEN a rank model is retrieved from file
    rank_model_dict = store.rank_model_from_url(rank_score_path)

    ## THEN the model is stored in the database
    assert store.rank_model_collection.find_one({"_id": rank_model_dict["_id"]})

    ## WHEN deleting the rank model
    result = runner.invoke(
        cli,
        [
            "delete",
            "rank-model",
            "--force",
            rank_score_path,
        ],
    )

    assert "Rank model delete successful" in result.output
    assert not store.rank_model_collection.find_one({"_id": rank_model_dict["_id"]})
