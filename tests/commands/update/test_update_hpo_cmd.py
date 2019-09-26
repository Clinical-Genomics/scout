# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store

def test_update_hpo(mock_app):
    """Tests the CLI that updates HPO terms in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(cli, ['update', 'hpo'])
    assert result.exit_code == 1
    assert 'Are you sure you want to drop the hpo terms?' in result.output

    # test propt confirm
    result =  runner.invoke(cli, ['update', 'hpo'],input='y')
    assert result.exit_code == 0
    assert 'INFO Time to load terms' in result.output


def test_update_hpo(mock_app):
    """Tests the CLI that updates HPO terms in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, no arguments provided
    result =  runner.invoke(cli, ['update', 'hpo'])
    assert result.exit_code == 1
    assert 'Are you sure you want to drop the hpo terms?' in result.output

    # test propt confirm
    result =  runner.invoke(cli, ['update', 'hpo'],input='y')
    assert result.exit_code == 0
    assert 'INFO Time to load terms' in result.output
