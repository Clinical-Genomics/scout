# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_export_hpo(mock_app):
    """Test the CLI command that exports genes based on HPO terms"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI without providing HPO terms
    result = runner.invoke(cli, ["export", "hpo_genes"])

    # The CLI command should return an error message then return abort code
    assert result.exit_code == 1
    assert "Please use at least one hpo term" in result.output

    # There are no HPO terms in database
    assert store.hpo_term_collection.find_one() is None
    # insert an HPO term in database:
    hpo_term = {
        "_id": "HP:0000003",
        "hpo_id": "HP:0000003",
        "hpo_number": 3,
        "description": "Multicystic kidney dysplasia",
        "genes": [17582, 1151],
    }
    store.hpo_term_collection.insert_one(hpo_term)
    assert sum(1 for i in store.hpo_term_collection.find()) == 1

    # Test CLI with a non-valid HPO term
    result = runner.invoke(cli, ["export", "hpo_genes", "non_HPO_term"])

    assert result.exit_code == 0
    assert "WARNING Term non_HPO_term could not be found" in result.output

    # Test CLI with a valid HPO term
    result = runner.invoke(cli, ["export", "hpo_genes", "HP:0000003"])

    assert result.exit_code == 0
    assert "17582\t1\n1151\t1\n" in result.output
