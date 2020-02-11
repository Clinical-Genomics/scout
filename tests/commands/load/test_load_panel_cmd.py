# -*- coding: utf-8 -*-

from scout.commands import cli
from scout.server.extensions import store


def test_load_panel(mock_app, institute_obj):
    """Test the CLI command that loads a gene panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    assert sum(1 for i in store.panel_collection.find()) == 1

    # Modify existing panel ID into OMIM-AUTO, so cli runner will not add it again
    store.panel_collection.find_one_and_update(
        {"panel_name": "panel1"}, {"$set": {"panel_name": "OMIM-AUTO"}}
    )

    # Test CLI by passing the panel 'OMIM-AUTO':
    result = runner.invoke(
        cli, ["load", "panel", "--api-key", "not_a_valid_key", "--omim"]
    )
    assert "OMIM-AUTO already exists in database" in result.output
