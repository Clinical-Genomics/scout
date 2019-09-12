# -*- coding: utf-8 -*-

from pymongo import IndexModel, ASCENDING

from scout.commands import cli
from scout.server.extensions import store

def test_delete_panel(mock_app):
    "Test the CLI command that deletes a gene panel"

    runner = mock_app.test_cli_runner()
    assert runner

    # Given a panel which is present in database
    db_panel = store.panel_collection.find_one()
    assert db_panel['panel_name']

    # Test the CLI that removes it by giving a wrong version
    result =  runner.invoke(cli, ['delete', 'panel',
        '--panel-id', db_panel['panel_name'],
        '-v', 5.0 # db_panel version is 1.0
        ])
    assert 'No panels found' in result.output

    # Test the CLI by using panel name without version
    result =  runner.invoke(cli, ['delete', 'panel',
        '--panel-id', db_panel['panel_name'],
        ])

    # Panel should be correctly removed from database
    assert 'WARNING Deleting panel {}'.format(db_panel['panel_name']) in result.output

    # And no panels ahould be available in database
    assert sum(1 for i in store.panel_collection.find()) == 0


def test_delete_index(mock_app):
    "Test the CLI command that will drop indexes"

    runner = mock_app.test_cli_runner()
    assert runner

    indexes = list(store.case_collection.list_indexes())
    assert len(indexes) > 1

    # Then remove all indexes using the CLI
    result =  runner.invoke(cli, ['delete', 'index'])

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
    assert sum(1 for i in store.user_collection.find()) == 1

    # Test the CLI command to remove users with a random email
    result =  runner.invoke(cli, ['delete', 'user', '-m', 'unknown_email@email.com'])

    # and the function should return error
    assert 'User unknown_email@email.com could not be found in database' in result.output

    # Try with a valid email
    result =  runner.invoke(cli, ['delete', 'user', '-m', user_obj['email']])

    # And the user should be gone
    assert result.exit_code == 0
    assert sum(1 for i in store.user_collection.find()) == 0


def test_delete_genes(mock_app):
    "Test the CLI command that will delete genes"

    runner = mock_app.test_cli_runner()
    assert runner

    # There are genes in genes collection in populated database
    assert sum(1 for i in store.hgnc_collection.find()) > 0

    # Test the CLI command to remove them with build option
    result =  runner.invoke(cli, ['delete', 'genes', '-b', '37'])

    # It should print "Dropping genes" message without actually dropping them (why??)
    assert result.exit_code == 0
    assert 'ropping genes collection for build: 37' in result.output
    assert sum(1 for i in store.hgnc_collection.find()) > 0

    # Test the CLI command to remove them without genome build
    result =  runner.invoke(cli, ['delete', 'genes'])

    # And it should actually drop them
    assert result.exit_code == 0
    assert sum(1 for i in store.hgnc_collection.find()) == 0


def test_delete_exons(mock_app):
    "Test the CLI command that will delete exons"

    runner = mock_app.test_cli_runner()
    assert runner

    # Exon collection in populated database is empty
    # Insert a mock exon object in database
    exon_objs = [
        {
            '_id' : 'mock_exon_1',
            'build' : '37'
        },
        {
            '_id' : 'mock_exon_2',
            'build' : '37'
        },
        {
            '_id' : 'mock_exon_3',
            'build' : '38'
        }
    ]
    store.exon_collection.insert_many(exon_objs)
    assert sum(1 for i in store.exon_collection.find()) == 3

    # Then use CLI to remove all exons with build == 38
    result =  runner.invoke(cli, ['delete', 'exons',
        '-b', '38'
        ])

    # the command should not exit with error
    # and one exon should be removed
    assert result.exit_code == 0
    assert sum(1 for i in store.exon_collection.find()) == 2

    # Use the CLI to remove all exons regardless:
    result =  runner.invoke(cli, ['delete', 'exons'])

    # and all exons should be removed
    assert result.exit_code == 0
    assert sum(1 for i in store.exon_collection.find()) == 0


def test_delete_case(mock_app, case_obj):
    "Test the CLI command that will delete a case"

    runner = mock_app.test_cli_runner()
    assert runner

    # Try to delete a case using CLI with no case_id or display_name
    result =  runner.invoke(cli, ['delete', 'case'])
    assert 'Please specify what case to delete' in result.output

    # try to delete case using CLI and case_id that doesn't exist in database
    result =  runner.invoke(cli, ['delete', 'case',
        '-i', case_obj['owner'],
        '-c', 'unknown_id'
        ])

    # and the program should terminate with error
    assert 'Case does not exist in database' in result.output

    # One case is available in database
    assert sum(1 for i in store.case_collection.find()) == 1

    # Provide right right case_id and institute
    result =  runner.invoke(cli, ['delete', 'case',
        '-c', case_obj['_id']
        ])
    assert result.exit_code == 0

    # and the case should be gone
    assert sum(1 for i in store.case_collection.find()) == 0

    # Re-insert case into database
    store.case_collection.insert_one(case_obj)
    assert sum(1 for i in store.case_collection.find()) == 1

    # Provide right display_name but not institute
    result =  runner.invoke(cli, ['delete', 'case',
        '-d', case_obj['display_name']
        ])
    assert result.exit_code == 1
    assert 'Please specify the owner of the case that should be deleted' in result.output

    # Provide right display_name and right institute
    result =  runner.invoke(cli, ['delete', 'case',
        '-d', case_obj['display_name'],
        '-i', case_obj['owner']
        ])

    # and the case should have been removed again
    assert result.exit_code == 0
    assert sum(1 for i in store.case_collection.find()) == 0
