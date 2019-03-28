# -*- coding: utf-8 -*-

from scout.commands import app_cli

from scout.server.extensions import store

def test_view_diseases(mock_app):
    """Test CLI that shows all collections in the database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI
    result =  runner.invoke(app_cli, ['view', 'collections'])
    assert result.exit_code == 0
    assert "collections\nexon\nhpo_term\ninstitute\ncase\nhgnc_gene\nuser\ngene_panel\nvariant\ntranscript\nevent\n" in result.output
