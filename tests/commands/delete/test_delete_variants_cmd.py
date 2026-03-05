from scout.commands import cli
from scout.server.extensions import store

VARIANTS_QUERY = {"rank_score": {"$lt": 0}}
RANK_THRESHOLD = 0
VARIANTS_THRESHOLD = 10


def test_delete_variants_dry_run(mock_app, case_obj, user_obj):
    """test command for cleaning variants collection - simulate deletion"""

    assert store.user_collection.find_one()

    # Given a database with SNV variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", case_obj["_id"], "--snv", "--rank-threshold", 5]
    )
    assert result.exit_code == 0
    n_initial_vars = sum(1 for _ in store.variant_collection.find())

    # Then the function that delete variants in dry run should run without error
    cmd_params = [
        "delete",
        "variants",
        "-u",
        user_obj["email"],
        "--status",
        "inactive",
        "--older-than",
        2,
        "--analysis-type",
        "wes",
        "--rank-threshold",
        RANK_THRESHOLD,
        "--variants-threshold",
        VARIANTS_THRESHOLD,
        "--keep-ctg",
        "str",
        "--dry-run",
    ]
    result = runner.invoke(cli, cmd_params)
    assert result.exit_code == 0
    assert "estimated deleted variants" in result.output

    # And no variants should be deleted
    assert sum(1 for _ in store.variant_collection.find()) == n_initial_vars


def test_delete_variants(mock_app, case_obj, user_obj):
    """Test deleting variants using the delete variants command line"""

    # Given a case with with SNV variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", "--snv", "--rank-threshold", 0, case_obj["_id"]]
    )
    assert result.exit_code == 0
    nr_snvs = sum(1 for _ in store.variant_collection.find())
    assert nr_snvs

    # AND WTS outliers
    result = runner.invoke(
        cli, ["load", "variants", "--outlier-research", case_obj["_id"], "--force"]
    )
    assert result.exit_code == 0
    nr_outliers = sum(1 for _ in store.omics_variant_collection.find())
    assert nr_outliers
    assert nr_outliers

    n_initial_vars = nr_snvs + nr_outliers

    # Then the function that delete variants should run without error
    cmd_params = [
        "delete",
        "variants",
        "-u",
        user_obj["email"],
        "--status",
        "inactive",
        "--keep-ctg",
        "outlier",
        "--older-than",
        2,
        "--analysis-type",
        "wes",
        "--rank-threshold",
        RANK_THRESHOLD,
        "--variants-threshold",
        VARIANTS_THRESHOLD,
    ]
    result = runner.invoke(cli, cmd_params, input="y")

    assert result.exit_code == 0
    assert "estimated deleted variants" not in result.output

    # variants should be deleted
    n_current_vars = sum(1 for _ in store.variant_collection.find())
    assert n_current_vars < n_initial_vars

    # and a relative event should be created
    event = store.event_collection.find_one({"verb": "remove_variants"})
    assert event["case"] == case_obj["_id"]
    assert (
        event["content"]
        == f"Rank-score threshold:{RANK_THRESHOLD}, case n. variants threshold:{VARIANTS_THRESHOLD}"
    )
    # SNV variants should be gone
    assert sum(1 for _ in store.variant_collection.find()) == 0

    # WHILE outliers should still be available
    assert sum(1 for _ in store.omics_variant_collection.find()) == nr_outliers


def test_delete_outlier_variants(mock_app, case_obj, user_obj):
    """Test the delete variants command's ability to remove omics variants."""

    # Given a case with with (research) outlier variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", "--snv", "--outlier-research", case_obj["_id"], "--force"]
    )
    assert result.exit_code == 0
    n_initial_vars = sum(1 for _ in store.omics_variant_collection.find())
    assert n_initial_vars
    n_variants_to_delete = store.omics_variant_collection.count_documents({})
    assert n_variants_to_delete

    # WHEN variants are removed using the command line
    cmd_params = [
        "delete",
        "variants",
        "-u",
        user_obj["email"],
        "--rank-threshold",
        0,
        "--rm-ctg",
        "outlier",
    ]
    result = runner.invoke(cli, cmd_params, input="y")
    assert result.exit_code == 0
    assert "estimated deleted variants" not in result.output

    # THEN the variants should be gone
    n_current_vars = sum(1 for _ in store.omics_variant_collection.find())
    assert n_current_vars == 0
    assert n_current_vars + n_variants_to_delete == n_initial_vars
    # and a relative event should be created
    event = store.event_collection.find_one({"verb": "remove_variants"})
    assert event["case"] == case_obj["_id"]
    assert "Rank-score threshold:0" in event["content"]
