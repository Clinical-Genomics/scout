from scout.commands import cli
from scout.commands.delete.variants import DELETE_VARIANTS_HEADER
from scout.server.extensions import store

VARIANTS_QUERY = {"rank_score": {"$lt": 0}}
RANK_THRESHOLD = 0
VARIANTS_THRESHOLD = 10


def test_delete_variants_dry_run(mock_app, case_obj, user_obj, tmp_path):
    """test command for cleaning variants collection - simulate deletion"""

    assert store.user_collection.find_one()

    # GIVEN a database with SNV variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", case_obj["_id"], "--snv", "--rank-threshold", 5]
    )
    assert result.exit_code == 0
    n_initial_vars = sum(1 for _ in store.variant_collection.find())

    # GIVEN a temp file path
    out_file = tmp_path / "variant_report.tsv"

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
        "--out-file",
        str(out_file),
    ]

    # THEN the function that delete variants in dry run should run without error
    result = runner.invoke(cli, cmd_params)
    assert result.exit_code == 0

    # THEN outfile should be populated
    file_content = out_file.read_text()
    # with the expected data
    assert "\t".join(DELETE_VARIANTS_HEADER) in file_content
    assert "estimated deleted variants" in file_content

    # And no variants should be deleted
    assert sum(1 for _ in store.variant_collection.find()) == n_initial_vars


def test_delete_variants(mock_app, case_obj, user_obj, tmp_path):
    """Test deleting variants using the delete variants command line"""

    # GIVEN a case with with SNV variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", "--snv", "--rank-threshold", 0, case_obj["_id"]]
    )
    assert result.exit_code == 0
    nr_snvs = sum(1 for _ in store.variant_collection.find())
    assert nr_snvs

    # GIVEN a temp file path
    out_file = tmp_path / "variant_report.tsv"

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
        "--out-file",
        str(out_file),
    ]
    result = runner.invoke(cli, cmd_params, input="y")

    assert result.exit_code == 0

    # THEN outfile should be populated
    file_content = out_file.read_text()
    # with the expected data
    assert "\t".join(DELETE_VARIANTS_HEADER) in file_content
    assert "estimated deleted variants" not in file_content

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


def test_delete_outlier_variants(mock_app, case_obj, user_obj, tmp_path):
    """Test the delete variants command's ability to remove omics variants."""

    # Given a case with with (research) outlier variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", "--outlier-research", case_obj["_id"], "--force"]
    )
    assert result.exit_code == 0
    n_initial_vars = sum(1 for _ in store.omics_variant_collection.find())
    assert n_initial_vars
    n_variants_to_delete = store.omics_variant_collection.count_documents({})
    assert n_variants_to_delete

    # GIVEN a temp file path
    out_file = tmp_path / "variant_report.tsv"

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
        "--out-file",
        str(out_file),
    ]
    result = runner.invoke(cli, cmd_params, input="y")
    assert result.exit_code == 0

    # THEN outfile should be populated
    file_content = out_file.read_text()
    # with the expected data
    assert "\t".join(DELETE_VARIANTS_HEADER) in file_content
    assert "estimated deleted variants" not in file_content

    # THEN the variants should be gone
    n_current_vars = sum(1 for _ in store.omics_variant_collection.find())
    assert n_current_vars == 0
    assert n_current_vars + n_variants_to_delete == n_initial_vars
    # and a relative event should be created
    event = store.event_collection.find_one({"verb": "remove_variants"})
    assert event["case"] == case_obj["_id"]
    assert "Rank-score threshold:0" in event["content"]
