import logging
from typing import Optional

import requests

API_PANELS_URL = "https://panelapp.genomicsengland.co.uk/api/v1/panels/"

LOG = logging.getLogger(__name__)


class PanelAppClient:
    """Class that retrieves PanelAll green genes using the NHS-NGS/panelapp library."""

    def __init__(self):
        self.panels_page = 1
        self.panel_types = set()
        self.panel_ids = []

    def get_panel_types(self) -> list:
        """Returns available panel types, collected from processed panels"""
        return sorted(list(self.panel_types))

    def get_panels(self, page: int, signed_off: bool = False) -> Optional[dict]:
        """Return a dictionary {panel_id: Panelapp.Panel} with all panels, signed off or not."""

        panels_url = f"{API_PANELS_URL}?page={page}"
        if signed_off:
            panels_url = f"{API_PANELS_URL}signedoff/?page={page}"

        resp = requests.get(panels_url, headers={"Content-Type": "application/json"})
        if not resp.ok:
            resp.raise_for_status()
            return

        return resp.json()

    def set_panel_types(self, json_panels: dict):
        """Collect available panel types from a page of panels and add them to the self.panel_types variable."""

        for panel in json_panels.get("results", []):
            for type in panel.get("types", []):
                self.panel_types.add(type["slug"])

    def get_panel_ids(self, signed_off: bool) -> list[int]:
        """Returns a list of panel ids contained in a json document with gene panels data."""

        def get_ids(json_panels):
            LOG.info(f"Retrieving IDs from API page {self.panels_page}")
            for panel in json_panels.get("results", []):
                self.panel_ids.append(panel["id"])
            self.panels_page += 1

        json_panels: dict = self.get_panels(
            signed_off=signed_off, page=self.panels_page
        )  # first page of results
        get_ids(json_panels=json_panels)
        self.set_panel_types(json_panels=json_panels)

        # Iterate over remaining pages of results
        while json_panels["next"] is not None:
            json_panels = self.get_panels(signed_off=signed_off, page=self.panels_page)
            get_ids(json_panels=json_panels)
            self.set_panel_types(json_panels=json_panels)

        return self.panel_ids

    def get_panel(self, panel_id: str) -> Optional[dict]:
        """Retrieve a gene_panel. Apply filters on panel type, if available."""
        panel_url = f"{API_PANELS_URL}{panel_id}"
        resp = requests.get(panel_url, headers={"Content-Type": "application/json"})
        if not resp.ok:
            resp.raise_for_status()
            return

        return resp.json()
