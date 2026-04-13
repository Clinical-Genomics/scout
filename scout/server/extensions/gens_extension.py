"""Code for Gens integration

* Requires gens version 1.1.1 or greater

GENS_DEFAULT_VERSION is the current major, and will be used if no other version is found.
The extension will attempt to find a version first in the scout app config, second by API call.
API calls will only find a version for gens v4 and onward.
"""

import logging

from scout.utils.scout_requests import get_request_json

LOG = logging.getLogger(__name__)
GENS_DEFAULT_VERSION = 3


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
        if version := app.config.get("GENS_VERSION"):
            self.version = version

    def connection_settings(self, genome_build: str = "37") -> dict:
        """Return information on where Gens is hosted.
        Check version if no version is set already. This needs to be done
        after authentication, so delaying until called from a Scout view.
        """
        settings = {}
        if self.host:
            base_url = f"{self.host}:{self.port}" if self.port else self.host
            settings = {
                "host": base_url,
                "genome_build": genome_build,
                "version": self.version if self.version else self.get_version(),
            }
        return {"display": bool(settings), **settings}

    def get_version(self) -> int:
        """Return gens version.

        The base API URL for Gens v4 has the version returned.
        The same page for v3 will return a Gens error page, though with status 200.
        """
        base_url = f"https://{self.host}:{self.port}" if self.port else self.host
        json_resp = get_request_json(f"{base_url}/api/")
        version = GENS_DEFAULT_VERSION
        content = json_resp.get("content", {})
        if json_resp.get("status_code") == 200 and "version" in content:
            version = int(content.get("version", "3")[0])
            self.version = version

        return version
