# -*- coding: utf-8 -*-

import json

import responses

from scout.commands import cli
from scout.demo import panel_path, panelapp_panel_path
from scout.server.extensions import store


def test_load_panel(mock_app):
    """Test the CLI command that loads a gene panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    assert sum(1 for _ in store.panel_collection.find()) == 1

    # Modify existing panel ID into OMIM-AUTO, so cli runner will not add it again
    store.panel_collection.find_one_and_update(
        {"panel_name": "panel1"}, {"$set": {"panel_name": "OMIM-AUTO"}}
    )

    # Test CLI by passing the panel 'OMIM-AUTO':
    result = runner.invoke(
        cli,
        [
            "load",
            "panel",
            "--maintainer",
            "john@doe.com",
            "--api-key",
            "not_a_valid_key",
            "--omim",
        ],
    )
    assert "OMIM-AUTO already exists in database" in result.output


@responses.activate
def test_load_panel_panelapp(mock_app):
    """Test loading a PanelApp gene panel"""

    # GIVEN a gene panel collection with one panel
    assert sum(1 for _ in store.panel_collection.find()) == 1

    # GIVEN a mocked response from PanelApp (mock response returns test PanelApp panel from scout/demo folder)
    panelapp_panel = 522
    data = None
    with open(panelapp_panel_path) as f:
        data = json.load(f)
    url = f"https://panelapp.genomicsengland.co.uk/WebServices/get_panel/{panelapp_panel}"
    responses.add(
        responses.GET,
        url,
        json=data,
        status=200,
    )

    # GIVEN an app CLI
    runner = mock_app.test_cli_runner()

    # Run command to load a PanelApp panel from the web
    result = runner.invoke(cli, ["load", "panel", "--panel-app", "--panel-id", panelapp_panel])

    # THEN panel should be loaded in database and the number of gene panels should increase by one
    assert result.exit_code == 0
    assert sum(1 for _ in store.panel_collection.find()) == 2

    # AND newly created gene panel should contain 2 genes: POT1 and MEGF8 (which is present in the json panel with the alias "C19orf49")
    panel_obj = store.panel_collection.find_one({"panel_name": str(panelapp_panel)})
    for gene in panel_obj["genes"]:
        assert gene["symbol"] in ["POT1", "MEGF8"]

    # Run the command again and it should not return error:
    result = runner.invoke(cli, ["load", "panel", "--panel-app", "--panel-id", panelapp_panel])
    assert result.exit_code == 0
    # Gene panels should still be the same, since PanelApp panel has been overwritten
    assert sum(1 for _ in store.panel_collection.find()) == 2


def test_load_panel_maintainer_not_in_db(mock_app):
    """Test the CLI command that loads a gene panel"""

    runner = mock_app.test_cli_runner()
    assert runner

    assert sum(1 for _ in store.panel_collection.find()) == 1

    # Test CLI by passing the panel 'OMIM-AUTO' - maintainer not in db!
    result = runner.invoke(
        cli,
        [
            "load",
            "panel",
            "--panel-id",
            "panel2",
            "--maintainer",
            "noone@no.no",
            panel_path,
        ],
    )
    assert "does not exist in user database" in result.output
