# -*- coding: utf-8 -*-

from pymongo import IndexModel, ASCENDING

from scout.commands import cli
from scout.server.extensions import store

VARIANTS_QUERY = {"rank_score": {"$lt": 15}}
RANK_THRESHOLD = 15
VARIANTS_THRESHOLD = 10


def test_delete_variants_dry_run(mock_app, case_obj, user_obj):
    """test command for cleaning variants collection - simulate deletion"""

    assert store.user_collection.find_one()

    # Given a database with SNV variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", case_obj["_id"], "--snv", "--rank-treshold", 5]
    )
    assert result.exit_code == 0
    n_initial_vars = sum(1 for i in store.variant_collection.find())

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
    assert "Estimated space freed" in result.output

    # And no variants should be deleted
    assert sum(1 for i in store.variant_collection.find()) == n_initial_vars


def test_delete_variants(mock_app, case_obj, user_obj):
    """Test deleting variants using the delete variants command line"""

    # Given a database with SNV variants
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli, ["load", "variants", case_obj["_id"], "--snv", "--rank-treshold", 5]
    )
    assert result.exit_code == 0
    n_initial_vars = sum(1 for i in store.variant_collection.find())
    n_variants_to_exclude = store.variant_collection.count_documents(VARIANTS_QUERY)

    # Then the function that delete variants should run without error
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
    ]
    result = runner.invoke(cli, cmd_params, input="y")
    assert result.exit_code == 0
    assert "estimated deleted variants" not in result.output
    assert "Estimated space freed" in result.output
    # variants should be deleted
    n_current_vars = sum(1 for i in store.variant_collection.find())
    assert n_current_vars < n_initial_vars
    assert n_current_vars + n_variants_to_exclude == n_initial_vars
    # and a relative event should be created
    event = store.event_collection.find_one()
    assert event["verb"] == "remove_variants"
    assert event["case"] == case_obj["_id"]
    assert (
        event["content"]
        == f"Rank-score threshold:{RANK_THRESHOLD}, case n. variants threshold:{VARIANTS_THRESHOLD}."
    )


def test_delete_panel_non_existing(empty_mock_app, dummypanel_obj):
    "Test the CLI command that deletes a gene panel"
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN database with a gene panel
    store.panel_collection.insert_one(dummypanel_obj)

    ## WHEN fetching giving a wrong version
    result = runner.invoke(
        cli,
        [
            "delete",
            "panel",
            "--panel-id",
            dummypanel_obj["panel_name"],
            "-v",
            5.0,  # db_panel version is 1.0
        ],
    )

    ## THEN assert no panel was found
    assert "No panels found" in result.output


def test_delete_panel(empty_mock_app, dummypanel_obj):
    "Test the CLI command that deletes a gene panel"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN database with a gene panel
    store.panel_collection.insert_one(dummypanel_obj)

    # Test the CLI by using panel name without version
    result = runner.invoke(cli, ["delete", "panel", "--panel-id", dummypanel_obj["panel_name"]])

    # Panel should be correctly removed from database
    assert "WARNING Deleting panel {}".format(dummypanel_obj["panel_name"]) in result.output

    # And no panels ahould be available in database
    assert sum(1 for i in store.panel_collection.find()) == 0


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


def test_delete_nonexisting_user(empty_mock_app, user_obj):
    "Test the CLI command that will delete a user"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN there is one user in populated database
    store.user_collection.insert_one(user_obj)
    assert store.user_collection.find_one()

    ## WHEN using the CLI command to remove users with a random email
    result = runner.invoke(cli, ["delete", "user", "-m", "unknown_email@email.com"])

    ## THEN function should return error
    assert "User unknown_email@email.com could not be found in database" in result.output


def test_delete_last_user_active_case(empty_mock_app, user_obj, case_obj, institute_obj):
    "Test the CLI command that will delete the last user of an active case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN there is one user in populated database
    store.user_collection.insert_one(user_obj)
    assert store.user_collection.find_one()

    ## And the user is an assignee of a case of an institute
    store.institute_collection.insert_one(institute_obj)

    ## And no events in the database
    assert store.event_collection.find_one() is None

    case_obj["assignees"] = [user_obj["email"]]
    case_obj["status"] = "active"
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one({"assignees": {"$in": case_obj["assignees"]}})

    ## WHEN deleting the user from the CLI
    result = runner.invoke(cli, ["delete", "user", "-m", user_obj["email"]])

    ## THEN the user should be gone
    assert result.exit_code == 0
    assert store.user_collection.find_one() is None

    # The case should be archived and should not have an assignee
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert updated_case["status"] == "inactive"
    assert updated_case["assignees"] == []

    ## And a new event for unassigning the user should have been created in event collection
    assert store.event_collection.find_one()


def test_delete_user_active_case(empty_mock_app, user_obj, case_obj, institute_obj):
    "Test the CLI command that will delete one of the users of an active case"

    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN there is one user in populated database
    store.user_collection.insert_one(user_obj)
    assert store.user_collection.find_one()

    ## And the user is an assignee of a case of an institute
    store.institute_collection.insert_one(institute_obj)

    ## And no events in the database
    assert store.event_collection.find_one() is None

    case_obj["assignees"] = [user_obj["email"], "user2@email"]
    case_obj["status"] = "active"
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one({"assignees": {"$in": case_obj["assignees"]}})

    ## WHEN deleting the user from the CLI
    result = runner.invoke(cli, ["delete", "user", "-m", user_obj["email"]])

    ## THEN the user should be gone
    assert result.exit_code == 0
    assert store.user_collection.find_one() is None

    # The case should NOT be inactivated and should still have the other assignee
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert updated_case["status"] == "active"
    assert updated_case["assignees"] == ["user2@email"]

    ## And a new event for unassigning the user should have been created in event collection
    assert store.event_collection.find_one()


def test_delete_last_user_solved_case(empty_mock_app, user_obj, case_obj, institute_obj):
    "Test the CLI command that will delete the last user of a solved case"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN there is one user in populated database
    store.user_collection.insert_one(user_obj)
    assert store.user_collection.find_one()

    ## And the user is an assignee of a case of an institute
    store.institute_collection.insert_one(institute_obj)

    ## And no events in the database
    assert store.event_collection.find_one() is None

    case_obj["assignees"] = [user_obj["email"]]
    case_obj["status"] = "solved"
    store.case_collection.insert_one(case_obj)
    assert store.case_collection.find_one({"assignees": {"$in": case_obj["assignees"]}})

    ## WHEN deleting the user from the CLI
    result = runner.invoke(cli, ["delete", "user", "-m", user_obj["email"]])

    ## THEN the user should be gone
    assert result.exit_code == 0
    assert store.user_collection.find_one() is None

    # The case should keep the original status and should not have an assignee
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert updated_case["status"] == "solved"
    assert updated_case["assignees"] == []

    ## And a new event for unassigning the user should have been created in event collection
    assert store.event_collection.find_one()


def test_delete_genes(empty_mock_app, gene_bulk):
    "Test the CLI command that will delete genes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN an adapter populated with genes
    assert store.hgnc_collection.find_one() is None
    store.hgnc_collection.insert_many(gene_bulk)
    assert store.hgnc_collection.find_one()

    ## WHEN removing them with CLI command
    result = runner.invoke(cli, ["delete", "genes", "-b", "37"])

    ## THEN should print "Dropping genes" message and drop all genes for build 37
    assert result.exit_code == 0
    assert "ropping genes collection for build: 37" in result.output
    assert store.hgnc_collection.find_one() is None


def test_delete_genes_one_build(empty_mock_app, gene_bulk_all):
    "Test the CLI command that will delete genes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN an adapter populated with genes
    assert store.hgnc_collection.find_one() is None
    store.hgnc_collection.insert_many(gene_bulk_all)
    assert store.hgnc_collection.find_one()

    ## WHEN removing them with CLI command
    result = runner.invoke(cli, ["delete", "genes", "-b", "37"])

    ## THEN should print "Dropping genes" message and drop all genes for build 37
    assert result.exit_code == 0
    assert "ropping genes collection for build: 37" in result.output
    ## THEN the genes from build 37 should be gone
    assert store.hgnc_collection.find_one({"build": "37"}) is None
    ## THEN the genes from build 38 should be left
    assert store.hgnc_collection.find_one({"build": "38"})


def test_delete_all_genes_both_builds(empty_mock_app, gene_bulk_all):
    "Test the CLI command that will delete genes"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    ## GIVEN an adapter populated with genes
    assert store.hgnc_collection.find_one() is None
    store.hgnc_collection.insert_many(gene_bulk_all)
    assert store.hgnc_collection.find_one()

    ## WHEN removing them with CLI command
    result = runner.invoke(cli, ["delete", "genes"])

    ## THEN should print "Dropping genes" message and drop all genes for build 37
    assert result.exit_code == 0
    assert "ropping all genes" in result.output
    ## THEN the genes from build 37 should be gone
    assert store.hgnc_collection.find_one() is None


def test_delete_exons_37(empty_mock_app):
    "Test the CLI command that will delete exons"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    exon_objs = [
        {"_id": "mock_exon_1", "build": "37"},
        {"_id": "mock_exon_2", "build": "37"},
        {"_id": "mock_exon_3", "build": "38"},
    ]
    ## GIVEN a database with some exons
    store.exon_collection.insert_many(exon_objs)
    assert store.exon_collection.find_one()

    ## WHEN using the CLI to remove all exons with build == 38
    result = runner.invoke(cli, ["delete", "exons", "-b", "38"])

    ## THEN the command should exit without errors
    assert result.exit_code == 0
    ## THEN there should be no exons with build 38
    assert store.exon_collection.find_one({"build": "38"}) is None
    ## THEN there should be exons left with build 37
    assert store.exon_collection.find_one({"build": "37"})

    # Use the CLI to remove all exons regardless:
    result = runner.invoke(cli, ["delete", "exons"])

    # and all exons should be removed
    assert result.exit_code == 0
    assert sum(1 for i in store.exon_collection.find()) == 0


def test_delete_exons(empty_mock_app):
    "Test the CLI command that will delete exons"
    mock_app = empty_mock_app

    runner = mock_app.test_cli_runner()
    assert runner

    exon_objs = [
        {"_id": "mock_exon_1", "build": "37"},
        {"_id": "mock_exon_2", "build": "37"},
        {"_id": "mock_exon_3", "build": "38"},
    ]
    ## GIVEN a database with some exons
    store.exon_collection.insert_many(exon_objs)
    assert store.exon_collection.find_one()

    ## WHEN using the CLI to remove all exons
    result = runner.invoke(cli, ["delete", "exons"])

    ## THEN the command should exit without errors
    assert result.exit_code == 0
    ## THEN there should be no exons left
    assert store.exon_collection.find_one() is None


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
    assert "Coudn't find any case in database matching the provided parameters" in result.output
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
    assert sum(1 for i in store.case_collection.find()) == 0


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
