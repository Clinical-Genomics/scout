"""
    Connect to BioNano Access server via it's API.

    https://bionano.com/wp-content/uploads/2023/01/30462-Bionano-Access-API-Guide-1.pdf
"""
import json
import logging
from typing import Dict, List, Optional

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

    def _get_token(self) -> Optional[Dict]:
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

        return json_content

    def _get_auth_cookies(self):
        """Parse and set authentication cookies based on a prepopulated values of token etc.
        Called after self._get_token, by methods that need cookies for accessing bionano-access.

        Returns:

        """
        cookies = {
            "token": self.bionano_token,
            "email": self.bionano_user_dict["email"],
            "fullname": self.bionano_user_dict["full_name"],
            "userpk": self.bionano_user_dict["userpk"],
            "userrole": self.bionano_user_dict["role"],
        }
        return cookies

    def _get_json(self, query):
        json_response = get_request_json(query, cookies=self._get_auth_cookies())

        json_content = json_response.get("content")
        if not json_content:
            return None
        LOG.debug("Response was %s", json_content)

        return json_content

    def _get_projects(self) -> Optional[List[Dict[str, str]]]:
        """Get a list of projects for the current bionano-access user."""
        projects = []
        query = f"{self.url}/Bnx/api/2.0/getProjects"

        LOG.info("List projects on BioNano Access")

        json_content = self._get_json(query)
        projects = json_content.get("output")

        return projects

    def _get_samples(self, project_uid) -> Optional[List[Dict[str, str]]]:
        """Get a list of samples for a given project uid."""
        samples = []
        query = f"{self.url}/Bnx/api/2.0/getSamples?projectuid={project_uid}"

        LOG.info("List samples on BioNano Access")

        json_content = self._get_json(query)
        samples = json_content.get("output")

        return samples

    def _get_uids_from_names(self, project_name, sample_name):
        """Get server UIDs given project name and sample name."""
        projects = self._get_projects()
        for project in projects:
            if project_name in project.get("name"):
                project_uid = project.get("projectuid")
                break

        samples = self._get_samples(project_uid)
        for sample in samples:
            if sample_name in sample.get("samplename"):
                sample_uid = sample.get("sampleuid")
                break
        return (project_uid, sample_uid)

    def _get_fshd_report(self, project_uid: str, sample_uid: str) -> Optional[List[Dict[str, str]]]:
        """Get FSHD report if available for the given project and sample."""
        report = {}

        query = (
            f"{self.url}/Bnx/api/2.0/getFSHDReport?projectuid={project_uid}&sampleuid={sample_uid}"
        )

        LOG.info("Get FSHD report from BioNano Access")
        json_content = self._get_json(query)
        report = json_content.get("content")

        return report

    def _parse_fshd_report(self, report: List[Dict[str, str]]) -> Optional[List[Dict[str, str]]]:
        """Parse BioNano FSHD report.
        Accepts a JSON iterable and returns an iterable with d4z4 loci dicts to display.
        """

        detailed_results = report.get("Detailed results")
        if not detailed_results:
            return None

        fshd_loci = []
        for result in detailed_results.get("value"):
            d4z4 = {}
            d4z4["map_id"] = result["MapID"]["value"]
            d4z4["chromosome"] = result["Chr"]["value"]
            d4z4["haplotype"] = result["Haplotype"]["value"]
            d4z4["count"] = result["Count_repeat"]["value"]
            d4z4["spanning_coverage"] = result["Repeat_spanning_coverage"]["value"]
            fshd_loci.append(d4z4)

        return fshd_loci

    def get_fshd_report(
        self, project_name: str, sample_name: str
    ) -> Optional[List[Dict[str, str]]]:
        """Retrieve FSHD report from a configured bionano access server.
        Accepts a project name and a sample name, and returns an iterable with d4z4 loci dicts to display.
        Returns None if access failed.
        """
        (project_uid, sample_uid) = self._get_uids_from_names(project_name, sample_name)

        report = self._get_fshd_report(project_uid, sample_uid)

        return self._parse_fshd_report(report)
