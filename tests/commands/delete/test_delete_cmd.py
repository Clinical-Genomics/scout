# -*- coding: utf-8 -*-
from scout.commands import cli
from scout.commands.delete.delete_command import CASE_RNA_KEYS
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


def test_delete_user_mme_submitter(
    empty_mock_app, user_obj, case_obj, institute_obj, mme_submission, mme_patient
):
    """Test deleting a user that is a contact for a MatchMaker Exchange case"""

    runner = empty_mock_app.test_cli_runner()
    user_email = user_obj["email"]

    # GIVEN a user in the database
    store.user_collection.insert_one(user_obj)

    ## GIVEN a case with an affected individual saved in MatchMaker
    store.institute_collection.insert_one(institute_obj)
    case_obj["individuals"] = [
        {"phenotype": 2, "individual_id": "ADM1059A2", "display_name": "NA12882"}
    ]
    mme_submission["patients"] = [mme_patient]
    case_obj["mme_submission"] = mme_submission
    store.case_collection.insert_one(case_obj)

    ## GIVEN that user_obj is the MME patient's contact
    updated_case = store.case_mme_update(case_obj, user_obj, mme_submission)
    # Submission contact should contain user's email
    assert updated_case["mme_submission"]["subm_user"] == user_email
    # And one associated event should be found in database
    assert store.event_collection.find_one({"verb": "mme_add", "user_id": user_email})

    # WHEN using the CLI command to remove the user, then the function should ask to reassign MME case
    result = runner.invoke(cli, ["delete", "user", "-m", user_email], input="n")
    # AND user shouldn't be removed if answer is no
    assert "Aborted" in result.output
    assert store.user_collection.find_one({"email": user_email})

    # User should also not be removed if answer provided is yes, but new contact doesn't exist
    non_existent_user = "foo@bar"
    result = runner.invoke(
        cli, ["delete", "user", "-m", user_email], input="\n".join(["y", non_existent_user])
    )
    assert f"User with email '{non_existent_user}' was not found" in result.output
    assert store.user_collection.find_one({"email": user_email})

    # GIVEN another user with no right over the MME submission
    new_users_email = "wonderwoman@dc.com"
    result = runner.invoke(
        cli,
        [
            "load",
            "user",
            "-i",
            institute_obj["_id"],
            "-u",
            "Diana Prince",
            "-m",
            new_users_email,
        ],
    )
    assert result.exit_code == 0

    # THEN if this user is provided as a new MME contact the remove command should fail again
    result = runner.invoke(
        cli, ["delete", "user", "-m", user_email], input="\n".join(["y", new_users_email])
    )
    assert (
        f"Scout user with email '{new_users_email}' doesn't have a 'mme_submitter' role"
        in result.output
    )
    assert store.user_collection.find_one({"email": user_email})

    # GIVEN that the new user has a "mme_submitter" role
    store.user_collection.find_one_and_update(
        {"email": new_users_email}, {"$set": {"roles": ["mme_submitter"]}}
    )
    # THEN the new user can be used as a new MME patient's contact
    result = runner.invoke(
        cli, ["delete", "user", "-m", user_email], input="\n".join(["y", new_users_email])
    )
    assert result.exit_code == 0
    # AND the old user should be removed
    assert store.user_collection.find_one({"email": user_email}) is None


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
