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
                "version": self.version or self.get_version(),
            }
        return {"display": bool(settings), **settings}

    def get_version(self) -> int:
        """Return gens version.

        The base API URL for Gens v4 has the version returned. Server could be https or http.
        The same page for v3 will return a Gens error page, though with status 200.
        """

        protocol = "https"
        base_url = (
            f"{protocol}://{self.host}:{self.port}" if self.port else f"{protocol}://{self.host}"
        )
        if version := self.get_version_from_api(base_url):
            return version

        protocol = "http"
        base_url = (
            f"{protocol}://{self.host}:{self.port}" if self.port else f"{protocol}://{self.host}"
        )
        if version := self.get_version_from_api(base_url):
            return version

        return GENS_DEFAULT_VERSION

    def get_version_from_api(self, base_url: str) -> int | None:
        """Check the version of Gens by making a request to the base API URL.
        This will only work for Gens v4 and onward, as earlier versions do not have this endpoint.
        Keep track if we received an authentication failure on the last try. Then it would be useful
        to make individual checks once the user is logged in."""

        json_resp = get_request_json(f"{base_url}/api/")
        content = json_resp.get("content", {})
        if json_resp.get("status_code") == 200 and "version" in content:
            version = int(content.get("version")[0])
            return version
        if json_resp.get("status_code") == 401:
            LOG.warning(
                "Authentication failure when trying to get Gens version. Gens is at least v4."
            )
            return 4
        return None
