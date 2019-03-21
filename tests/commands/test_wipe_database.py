# -*- coding: utf-8 -*-

from scout.commands import app_cli
from scout.server.extensions import store

def test_wipe_database_cmd(mock_app):
    """Testing the wipe database cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    database_name = mock_app.config["MONGO_DBNAME"]
    assert database_name

    # test CLI to wipe out database
    result =  runner.invoke(app_cli, ['wipe'], input='y')
    assert result.exit_code == 0
    assert 'Dropped whole database' in result.output
