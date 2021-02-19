"""Code for Rerunner integration."""
import logging

LOG = logging.getLogger(__name__)


class RerunnerService:
    """Interface to Rerunner."""

    def __init__(self):
        self.host = None
        self.port = None

    def init_app(self, app):
        """Setup Rerunner config."""
        LOG.info("Init Rerunner app")
        self.host = app.config.get("RERUNNER_HOST")
        self.port = app.config.get("RERUNNER_PORT")
        self.timeout = app.config.get("RERUNNER_TIMEOUT", 10)
        self.api_key = app.config.get("RERUNNER_API_KEY")

    @property
    def connection_settings(self):
        """Return information on where Rerunner is hosted.

        Args:
            build(str): "37" or "38"

        Returns:
            rerunner_info(dict): A dictionary containing information on where Rerunner if hosted.
        """
        settings = {}
        if self.host and self.api_key:
            settings = {
                "host": f"{self.host}:{self.port}" if self.host and self.port else self.host,
                "api_key": self.api_key,
            }
        return {"display": bool(settings), **settings}
