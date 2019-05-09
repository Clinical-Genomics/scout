# -*- coding: utf-8 -*-

from scout.commands import app_cli
from scout.server.extensions import store

def test_view_hpo(mock_app):
    """Test CLI that shows all HPO terms in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(app_cli, ['view', 'hpo'])
    assert result.exit_code == 0
    # no term shold be returned
    assert "No matching terms found" in result.output

    # no HPO terms in database, so insert one
    assert store.hpo_term_collection.find().count() == 0
    hpo_term = {
        '_id' : 'HP:0000311',
        'hpo_id' : 'HP:0000311',
        'hpo_number' : 311,
        'description' : 'Round face',
        'genes' : [4392, 30832],
    }
    store.hpo_term_collection.insert(hpo_term)

    # Test CLI providing a term
    result =  runner.invoke(app_cli, ['view', 'hpo',
        '-t', 'HP:0000311'
        ])
    assert result.exit_code == 0
    # Term should be found
    assert "Found 1 terms" in result.output

    # Test CLI by providing HPO term not starting with 'HP00..'
    result =  runner.invoke(app_cli, ['view', 'hpo',
        '-t', '311'
        ])
    assert result.exit_code == 0
    # Term should be found
    assert "Found 1 terms" in result.output

    # Test CLI by providing HPO term description
    result =  runner.invoke(app_cli, ['view', 'hpo',
        '-d', 'face'
        ])
    assert result.exit_code == 0
    # Term should be found
    assert "Found 1 terms" in result.output

    # Test CLI with --json flag
    result =  runner.invoke(app_cli, ['view', 'hpo','-j'])
    assert result.exit_code == 0
    # Output should be in json format
    assert '{"_id": "HP:0000311", "hpo_id": "HP:0000311"' in result.output
