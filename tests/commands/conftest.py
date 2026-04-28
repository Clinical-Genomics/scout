"""Fixtures for CLI tests"""

import json
import pathlib
from typing import Any, Callable, Dict

import pytest

from scout.demo.resources import demo_files, panelapp_all_reduced_path

#############################################################
###################### App fixtures #########################
#############################################################
# use this app object to test CLI commands which use a test database

DATABASE = "testdb"
REAL_DATABASE = "realtestdb"


@pytest.fixture(scope="function", name="demo_files")
def fixture_demo_files():
    """Return a dictionary with paths to the demo files"""
    return demo_files


@pytest.fixture
def panelapp_panel_lookup() -> Callable[[int], Dict[str, Any]]:
    """Return a panel given its ID."""
    path = panelapp_all_reduced_path

    with open(path, "r", encoding="utf-8") as f:
        panels = [json.loads(line) for line in f if line.strip()]

    panel_map = {panel["id"]: panel for panel in panels}

    def _lookup(panel_id: int) -> Dict[str, Any]:
        return panel_map[panel_id]

    return _lookup


@pytest.fixture
def panelapp_api_panel(panelapp_panel_lookup) -> dict:
    """Return one panel as it would be returned by the PanelApp API."""
    return panelapp_panel_lookup(522)


@pytest.fixture(scope="function")
def bam_path():
    """Return the path to a small existing bam file"""
    _path = pathlib.Path("tests/fixtures/bams/reduced_mt.bam")
    return _path
