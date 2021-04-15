# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_view_diseases(mock_app):
    """Test CLI that shows all diseases in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI
    result = runner.invoke(cli, ["view", "diseases"])
    assert result.exit_code == 0
    # NO OMIM term should be preloaded in database
    assert "No diseases found" in result.output

    # insert one in database
    omim_term = {
        "_id": "OMIM:193040",
        "disease_id": "OMIM:193040",
        "description": "Cholestasis progressive canalicular",
        "source": "OMIM",
        "genes": [12690],
        "inheritance": None,
        "hpo_terms": None,
    }
    store.disease_term_collection.insert_one(omim_term)

    # Test CLI
    result = runner.invoke(cli, ["view", "diseases"])
    assert result.exit_code == 0
    # OMIM disease should now be found
    assert "OMIM:193040" in result.output
