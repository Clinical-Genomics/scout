"""
    Connect to BioNano Access server via it's API.

    https://bionano.com/wp-content/uploads/2023/01/30462-Bionano-Access-API-Guide-1.pdf
"""
import datetime
import json
import logging

from scout.utils.scout_requests import get_request_json

LOG = logging.getLogger(__name__)


class BioNanoAccessAPI:
    """Use BioNano Access API to retrieve reports."""

    def __init__(self):
        self.url = None
        self.bionano_username = None
        self.bionano_password = None
        self.bionano_token = None
        self.bionano_user_dict = None

    def init_app(self, app):
        self.url = app.config.get("BIONANO_ACCESS")
        self.bionano_username = app.config.get("BIONANO_USERNAME")
        self.bionano_password = app.config.get("BIONANO_PASSWORD")
        _get_token(self)

    def _get_token(self):
        query = f"{self.url}/administration/api/1.4/login?user={self.bionano_username}&password={self.bionano_password}"

        LOG.info("Authenticating for BioNano Access")
        json_response = get_request_json(query)

        json_content = json_response.get("content")
        if not json_content:
            return None
        LOG.info("Response was %s", json_content)
        json_content = json_content[0]

        if "user" in json_content:
            self.bionano_user_dict = json_content["user"]
        if "token" in json_content:
            self.bionano_token = json_content["token"]

    def _get_projects(self):
        query = f"{self.url}/Bnx/api/2.0/getProjects"

        cookies = {"user": self.bionano_user_dict, "token": self.bionano_token}

        LOG.info("List projects on BioNano Access")
        json_response = get_request_json(query)

        json_content = json_response.get("content")
        if not json_content:
            return None
        LOG.info("Response was %s", json_content)
        json_content = json_content[0]

    def load_report(self, institute, sample):
        _get_projects()

        _get_samples()

        _get_fshd_report(project_uid, sample_uid)
