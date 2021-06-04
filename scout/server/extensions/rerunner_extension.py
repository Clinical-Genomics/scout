"""Code for Rerunner integration."""
import logging

LOG = logging.getLogger(__name__)


class RerunnerService:
    """Interface to Rerunner."""

    def __init__(self):
        self.entrypoint = None
        self.api_key = None

    def init_app(self, app):
        """Setup Rerunner config."""
        LOG.info("Init Rerunner app")
        self.entrypoint = app.config.get("RERUNNER_API_ENTRYPOINT")
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
        if self.entrypoint and self.api_key:
            settings = {
                "entrypoint": self.entrypoint,
                "api_key": self.api_key,
            }
        return {"display": bool(settings), **settings}


class RerunnerError(Exception):
    pass
