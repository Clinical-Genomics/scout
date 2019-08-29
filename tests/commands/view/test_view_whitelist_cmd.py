# -*- coding: utf-8 -*-

from scout.commands import cli

from scout.server.extensions import store


def test_view_witelist(mock_app):
    """Test the CLI that shows all objects in the whitelist collection"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI
    result =  runner.invoke(cli, ['view', 'whitelist'])
    assert result.exit_code == 0
    assert 'INFO Running scout view users' in result.output

    # insert mock obj in whitelist collection
    store.whitelist_collection.insert_one({'_id' : 'fake_whitelist_id'})

    # Test CLI
    result =  runner.invoke(cli, ['view', 'whitelist'])
    assert result.exit_code == 0
    # mock obj should be returned
    assert 'fake_whitelist_id' in result.output
