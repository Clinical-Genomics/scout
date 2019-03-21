# -*- coding: utf-8 -*-

from scout.commands import app_cli

def test_load_research(mock_app, case_obj):
    """Testing the load research cli command"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test command without case_id:
    result =  runner.invoke(app_cli, ['load', 'research'])
    assert result.exit_code == 0
    assert "Get cases with query {'research_requested': True}" in result.output

    # Test command providing a case_id:
    result =  runner.invoke(app_cli, ['load', 'research',
        '-c', case_obj['_id']])
    assert result.exit_code == 0

    # Test command providing case_id, institute and force flag:
    result =  runner.invoke(app_cli, ['load', 'research',
        '-c', case_obj['_id'],
        '-i', case_obj['owner'],
        '-f'
        ])
    assert result.exit_code == 0
