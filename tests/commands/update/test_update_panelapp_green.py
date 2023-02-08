"""Tests for scout update panelapp-green command"""

import json

import responses

from scout.commands import cli
from scout.demo import panelapp_panel_path
from scout.load.panel import PANEL_NAME, PANELAPP_BASE_URL
from scout.server.extensions import store

DEMO_PANEL = "522"
PANELAPP_LIST_PANELS_URL = PANELAPP_BASE_URL.format("list_panels")
PANELAPP_GET_PANEL_URL = PANELAPP_BASE_URL.format("get_panel") + str(DEMO_PANEL)


def test_update_panelapp_green_non_existing_institute(empty_mock_app):
    """Tests the CLI that updates PANELAPP-GREEN panel in database, when provided institute id doesn't exist"""

    mock_app = empty_mock_app

    # GIVEN a cli runner
    runner = mock_app.test_cli_runner()
    assert runner

    # WHEN updating panelapp_green with an institute id that is not found in the database
    result = runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000"])
    # THEN warns that institute does not exist
    assert "Please specify an existing institute" in result.output
    # AND command raises error
    assert result.exit_code != 0


@responses.activate
def test_update_panelapp_green(mock_app):
    """Tests the CLI that creates/updates PANELAPP-GREEN panel in database"""

    # GIVEN that no PANELAPP-GREEN panel exists in database:
    assert store.gene_panel(panel_id=PANEL_NAME) is None

    # GIVEN a mocked response from PanelApp list_panels endpoint
    responses.add(
        responses.GET,
        PANELAPP_LIST_PANELS_URL,
        json={"result": [{"Panel_Id": DEMO_PANEL}]},
        status=200,
    )

    # GIVEN a mocked response from PanelApp get_panel endpoint (mock response returns test PanelApp panel from scout/demo folder)
    data = None
    with open(panelapp_panel_path) as f:
        data = json.load(f)
    responses.add(
        responses.GET,
        PANELAPP_GET_PANEL_URL,
        json=data,
        status=200,
    )

    # GIVEN an app CLI
    runner = mock_app.test_cli_runner()

    # THEN command to create the PANELAPP-GREEN panel should be successful
    result = runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000"])
    assert result.exit_code == 0

    # AND the panel should have been saved in databsse
    green_panel = store.gene_panel(panel_id=PANEL_NAME)
    assert green_panel
    assert green_panel["genes"]

    # GIVEN that the old saved panel contains one extra gene
    extra_gene = {"hgnc_id": 7227, "symbol": "MRAS"}
    store.panel_collection.find_one_and_update(
        {"panel_name": PANEL_NAME}, {"$push": {"genes": extra_gene}}
    )

    # WHEN panel is updated without the force flag
    runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000"])

    # THEN PanelApp Green panel should NOT be updated
    assert store.gene_panel(panel_id=PANEL_NAME)["version"] == green_panel["version"]

    # WHEN updating the panel with the force flag
    runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000", "-f"])

    # THEN PanelApp Green panel should be updated
    assert store.gene_panel(panel_id=PANEL_NAME)["version"] > green_panel["version"]
