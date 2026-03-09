"""Code for Gens integration

* Requires gens version 1.1.1 or greater
"""

import logging

from scout.utils.scout_requests import get_request_json

LOG = logging.getLogger(__name__)
GENS_DEFAULT_VERSION = 4


class GensViewer:
    """Interface to Gens."""

    def __init__(self):
        self.host = None
        self.port = None
        self.version: int | None = None

    def init_app(self, app):
        """Setup Gens config."""
        LOG.info("Init Gens app")
        self.host = app.config.get("GENS_HOST")
        self.port = app.config.get("GENS_PORT")
        self.version = app.config.get("GENS_VERSION", GENS_DEFAULT_VERSION)

    def connection_settings(self, genome_build="37"):
        """Return information on where GENS is hosted.

        Args:
            build(str): "37" or "38"

        Returns:
            gens_info(dict): A dictionary containing information on where Gens if hosted.
        """
        settings = {}
        if self.host:
            base_url = f"{self.host}:{self.port}" if self.port else self.host
            settings = {
                "host": base_url,
                "genome_build": genome_build,
                "version": self.version,
            }
        return {"display": bool(settings), **settings}

    def gens_version(self) -> str:
        base_url = f"{self.host}:{self.port}" if self.port else self.host
        json_resp = get_request_json(base_url + "/api/")
        if json_resp.get("status_code") == 200:
            version = 4

        return version
