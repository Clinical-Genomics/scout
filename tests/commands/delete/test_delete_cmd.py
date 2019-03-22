# -*- coding: utf-8 -*-

from pymongo import IndexModel, ASCENDING

from scout.commands import app_cli
from scout.server.extensions import store

def test_delete_panel(mock_app):
    "Test the CLI command that deletes a gene panel"

    runner = mock_app.test_cli_runner()
    assert runner

    # Given a panel which is present in database
    db_panel = store.panel_collection.find_one()
    assert db_panel['panel_name']

    # Test the CLI that removes it by giving a wrong version
    result =  runner.invoke(app_cli, ['delete', 'panel',
        '--panel-id', db_panel['panel_name'],
        '-v', 5.0 # db_panel version is 1.0
        ])
    assert 'No panels found' in result.output

    # Test the CLI by using panel name without version
    result =  runner.invoke(app_cli, ['delete', 'panel',
        '--panel-id', db_panel['panel_name'],
        ])

    # Panel should be correctly removed from database
    assert 'WARNING Deleting panel {}'.format(db_panel['panel_name']) in result.output

    # And no panels ahould be available in database
    assert store.panel_collection.find().count() == 0


def test_delete_index(mock_app):
    "Test the CLI command that will drop indexes"

    runner = mock_app.test_cli_runner()
    assert runner

    indexes = list(store.case_collection.list_indexes())
    assert len(indexes) > 1

    # Then remove all indexes using the CLI
    result =  runner.invoke(app_cli, ['delete', 'index'])

    # The function should not exit with error
    assert result.exit_code == 0
    assert 'All indexes deleted' in result.output

    # And the index should be gone
    indexes = list(store.case_collection.list_indexes())
    assert len(indexes) == 1 # _id index is the only index left


def test_delete_user(mock_app, user_obj):
    "Test the CLI command that will delete a user"

    runner = mock_app.test_cli_runner()
    assert runner

    # There is one user in populated database
    assert store.user_collection.find().count() == 1

    # Test the CLI command to remove users with a random email
    result =  runner.invoke(app_cli, ['delete', 'user', '-m', 'unknown_email@email.com'])

    # and the function should return error
    assert 'User unknown_email@email.com could not be found in database' in result.output

    # Try with a valid email
    result =  runner.invoke(app_cli, ['delete', 'user', '-m', user_obj['email']])

    # And the user should be gone
    assert result.exit_code == 0
    assert store.user_collection.find().count() == 0


def test_delete_genes(mock_app):
    "Test the CLI command that will delete genes"

    runner = mock_app.test_cli_runner()
    assert runner

    # There are genes in genes collection in populated database
    assert store.hgnc_collection.find().count() > 0

    # Test the CLI command to remove them with build option
    result =  runner.invoke(app_cli, ['delete', 'genes', '-b', '37'])

    # It should print "Dropping genes" message without actually dropping them (why??)
    assert result.exit_code == 0
    assert 'ropping genes collection for build: 37' in result.output
    assert store.hgnc_collection.find().count() > 0

    # Test the CLI command to remove them without genome build
    result =  runner.invoke(app_cli, ['delete', 'genes'])

    # And it should actually drop them
    assert result.exit_code == 0
    assert store.hgnc_collection.find().count() == 0






    #
    #assert store.hgnc_collection.find().count() == 0
