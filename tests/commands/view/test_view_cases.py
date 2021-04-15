# -*- coding: utf-8 -*-

import pymongo

from scout.commands import cli
from scout.server.extensions import store

DB_PARAMS = ["-db", "realtestdb"]


def test_view_cases(mock_app, case_obj, test_hpo_terms):
    """Tests the CLI that displays cases from the database"""

    adapter = store
    # Given a real populated database with a case
    assert sum(1 for i in adapter.case_collection.find()) == 1

    # Create a test CLI runner
    runner = mock_app.test_cli_runner()
    assert runner

    # and test the CLI base, no arguments provided
    result = runner.invoke(cli, ["view", "cases"])
    # Command should not exit with error
    assert result.exit_code == 0
    # and the test case should be returned
    assert "643594" in result.output

    # Test CLI base providing an institute not in database
    result = runner.invoke(cli, ["view", "cases", "-i", "cust666"])
    assert result.exit_code == 0
    # test case should NOT be returned
    assert "No cases could be found" in result.output

    # Test CLI base providing an existing institute
    result = runner.invoke(cli, ["view", "cases", "-i", "cust000"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # Test CLI base providing display name
    result = runner.invoke(cli, ["view", "cases", "-d", "643594"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # Test CLI base providing case _id
    result = runner.invoke(cli, ["view", "cases", "-c", "internal_id"])
    assert result.exit_code == 0
    # test case should be returned
    assert "643594" in result.output

    # load research variants for this case:
    result = runner.invoke(cli, ["load", "variants", "internal_id", "--snv"])
    assert result.exit_code == 0
    # variants should have been loaded to database
    n_vars = sum(1 for i in adapter.variant_collection.find())
    assert n_vars > 0

    # Test CLI with --nr-variants flag
    result = runner.invoke(cli, ["view", "cases", "-c", "internal_id", "--nr-variants"])
    assert result.exit_code == 0
    # number of variants should be shown in output
    assert str(n_vars) in result.output

    # Test CLI with --variants-treshold param
    result = runner.invoke(cli, ["view", "cases", "--variants-treshold", n_vars])
    assert result.exit_code == 0
    # number of variants should be shown in output
    assert str(n_vars) in result.output

    # Test CLI with --variants-treshold param
    result = runner.invoke(cli, ["view", "cases", "--variants-treshold", n_vars + 1])
    assert result.exit_code == 0
    # number of variants should be shown in output
    assert "Displaying number of variants for each case" in result.output

    # Testing CLI command to get similar cases when no other case
    # with phenotype is available
    result = runner.invoke(cli, ["view", "cases", "-c", "internal_id", "--similar"])
    # command should run
    assert result.exit_code == 0
    # and return INFO message
    assert "INFO No more cases with phenotypes found" in result.output

    # update test case using test HPO terms
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
        return_document=pymongo.ReturnDocument.AFTER,
    )

    # insert another case in database with a slighly different phenotype
    case_obj["_id"] = "case_2"
    case_obj["phenotype_terms"] = test_hpo_terms[:-1]  # exclude last term

    # insert this case in database:
    adapter.case_collection.insert_one(case_obj)
    assert sum(1 for i in adapter.case_collection.find()) == 2

    # Test CLI to get similar cases to test patient
    result = runner.invoke(cli, ["view", "cases", "-c", "internal_id", "--similar"])
    assert result.exit_code == 0
    # Table with case_id and score should be returned
    assert "#case_id\tscore\n" in result.output
