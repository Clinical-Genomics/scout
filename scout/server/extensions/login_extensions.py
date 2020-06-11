import logging
from oauthlib.oauth2 import WebApplicationClient

LOG = logging.getLogger(__name__)


class GoogleApplicationClient(WebApplicationClient):
    """Class handling the Google login system"""

    def __init__(self):
        LOG.debug("Setting up Google login manager")

    def init_app(self, app):
        client_id = app.config["GOOGLE"].get("client_id")
        super().__init__(client_id)
