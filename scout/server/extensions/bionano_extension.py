"""
    Connect to BioNano Access server via it's API.

    https://bionano.com/wp-content/uploads/2023/01/30462-Bionano-Access-API-Guide-1.pdf
"""
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

        self._get_token()

    def _get_token(self):
        query = f"{self.url}/administration/api/1.4/login?username={self.bionano_username}&password={self.bionano_password}"

        LOG.info("Authenticating for BioNano Access")
        json_response = get_request_json(query)

        json_content = json_response.get("content")
        if not json_content:
            return None
        LOG.info("Response was %s", json_content)
        json_output = json_content.get("output")

        if "user" in json_content:
            self.bionano_user_dict = json_output.get("user")
        if "token" in json_content:
            self.bionano_token = json_output.get("token")

    def _get_auth_cookies(self):
        cookies = {
            "token": self.bionano_token,
            "email": self.bionano_user_dict["email"],
            "fullname": self.bionano_user_dict["full_name"],
            "userpk": self.bionano_user_dict["userpk"],
            "userrole": self.bionano_user_dict["role"],
        }
        return cookies

    def _get_projects(self):
        projects = []
        query = f"{self.url}/Bnx/api/2.0/getProjects"

        LOG.info("List projects on BioNano Access")
        json_response = get_request_json(query, cookies=self._get_auth_cookies())

        json_content = json_response.get("content")
        if not json_content:
            return None
        LOG.info("Response was %s", json_content)

        projects = json_content.get("output")

        return projects

    def _get_samples(self, project_uid):
        samples = []
        query = f"{self.url}/Bnx/api/2.0/getSamples?projectuid={project_uid}"

        LOG.info("List samples on BioNano Access")
        json_response = get_request_json(query, cookies=self._get_auth_cookies())

        json_content = json_response.get("content")
        if not json_content:
            return None
        LOG.info("Response was %s", json_content)

        samples = json_content.get("output")

        return samples

    def _get_FSHD_report(self, project_uid, sample_uid):
        report = {}

        query = (
            f"{self.url}/Bnx/api/2.0/getFSHDReport?projectuid={project_uid}&sampleuid={sample_uid}"
        )

        cookies = {"user": self.bionano_user_dict, "token": self.bionano_token}

        LOG.info("List samples on BioNano Access")
        json_response = get_request_json(query)

        json_content = json_response.get("content", cookies=self._get_auth_cookies())
        if not json_content:
            return None
        LOG.info("Response was %s", json_content)

        report = json_content.get("content")

        return report

    def get_FSHD_report(self, institute, sample):
        projects = self._get_projects()
        for project in projects:
            if institute in project.get("name"):
                project_uid = project.get("projectuid")
                continue

        samples = self._get_samples(project_uid)
        for sample in samples:
            if sample in sample.get("samplename"):
                sample_uid = sample.get("sampleuid")
                continue

        report = self._get_FSHD_report(project_uid, sample_uid)

        return report
