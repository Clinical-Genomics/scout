import logging
import time
from typing import List, Optional

import requests

API_PANELS_URL = "https://panelapp.genomicsengland.co.uk/api/v1/panels/"

LOG = logging.getLogger(__name__)


def _get_with_retry_after(url, headers=None, max_retries=5):
    """GET wrapper that respects PanelApp 429 Retry-After."""
    attempts = 0
    while True:
        resp = requests.get(url, headers=headers or {})
        if resp.status_code in (200, 304):
            return resp

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            try:
                wait = int(retry_after) if retry_after else 60
            except ValueError:
                wait = 60

            LOG.warning(
                f"PanelApp rate limit reached (429). Waiting {wait}s "
                f"(attempt {attempts+1}/{max_retries})"
            )
            time.sleep(wait)
            attempts += 1
            if attempts >= max_retries:
                raise RuntimeError("Too many 429 responses from PanelApp")
            continue

        resp.raise_for_status()


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

        resp = _get_with_retry_after(panels_url, headers={"Content-Type": "application/json"})

        return resp.json()

    def set_panel_types(self, json_panels: dict):
        """Collect available panel types from a page of panels and add them to the self.panel_types variable."""

        for panel in json_panels.get("results", []):
            for type in panel.get("types", []):
                self.panel_types.add(type["slug"])

    def get_panel_ids(self, signed_off: bool) -> List[int]:
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
        resp = _get_with_retry_after(panel_url, headers={"Content-Type": "application/json"})

        return resp.json()
