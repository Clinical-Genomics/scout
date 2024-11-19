"""Tests for scout update panelapp-green command"""

import json

import responses

from scout.commands import cli
from scout.demo import panelapp_panel_path, panelapp_panels_reduced_path
from scout.load.panelapp import PANEL_NAME
from scout.server.extensions import store
from scout.server.extensions.panelapp_extension import API_PANELS_URL

DEMO_PANEL = "522"
PANELAPP_GET_PANEL_URL = f"{API_PANELS_URL}{DEMO_PANEL}"


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
def test_update_green_panel(mock_app):
    """Tests the CLI that creates/updates PANELAPP-GREEN panel in database"""

    # GIVEN that no PANELAPP-GREEN panel exists in database:
    assert store.gene_panel(panel_id=PANEL_NAME) is None

    # GIVEN a mocked response from PanelApp list_panels endpoint
    with open(panelapp_panels_reduced_path) as f:
        panels_data = json.load(f)

    responses.add(
        responses.GET,
        API_PANELS_URL,
        json=panels_data,
        match=[responses.matchers.header_matcher({"Content-Type": "application/json"})],
        status=200,
    )

    # GIVEN a mocked response from PanelApp get_panel endpoint (mock response returns test PanelApp panel from scout/demo folder)
    with open(panelapp_panel_path) as f:
        panel_data = json.load(f)
    responses.add(
        responses.GET,
        PANELAPP_GET_PANEL_URL,
        json=panel_data,
        match=[responses.matchers.header_matcher({"Content-Type": "application/json"})],
        status=200,
    )

    # GIVEN a cli runner
    runner = mock_app.test_cli_runner()
    assert runner

    # THEN command to create the PANELAPP-GREEN panel should be successful
    result = runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000"], input="1")

    assert result.exit_code == 0

    # AND the panel should have been saved in database
    green_panel = store.gene_panel(panel_id=PANEL_NAME)

    # GIVEN that the old saved panel contains one extra gene
    extra_gene = {"hgnc_id": 7227, "symbol": "MRAS"}
    store.panel_collection.find_one_and_update(
        {"panel_name": PANEL_NAME}, {"$push": {"genes": extra_gene}}
    )

    # WHEN panel is updated without the force flag
    runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000"], input="1")

    # THEN PanelApp Green panel should NOT be updated
    assert store.gene_panel(panel_id=PANEL_NAME)["version"] == green_panel["version"]

    # WHEN updating the panel with the force flag
    runner.invoke(cli, ["update", "panelapp-green", "-i", "cust000", "-f"], input="1")

    # THEN PanelApp Green panel should be updated
    assert store.gene_panel(panel_id=PANEL_NAME)["version"] > green_panel["version"]
