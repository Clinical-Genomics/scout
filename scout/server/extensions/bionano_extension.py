"""
    Connect to BioNano Access server via its API.

    The server API we connect to is described in the following document:
    https://bionano.com/wp-content/uploads/2023/01/30462-Bionano-Access-API-Guide-1.pdf
    For further development, the server has a Swagger-like demo interface at https://bionano-access.scilifelab.se/Bnx/
    which is useful for details, and for sniffing actual message content structure, required cookie variable names etc.
"""
import json
import logging
from typing import Dict, Iterable, List, Optional, Tuple

from flask import flash

from scout.utils.convert import call_safe
from scout.utils.scout_requests import get_request_json

LOG = logging.getLogger(__name__)

NO_BIONANO_FSHD_REPORT_FLASH_MESSAGE = (
    "BioNano Access server could not find any FSHD reports for this sample."
)


class BioNanoAccessAPI:
    """Use BioNano Access API to retrieve reports."""

    def __init__(self):
        self.url = None
        self.bionano_username = None
        self.bionano_password = None
        self.bionano_token = None
        self.bionano_user_dict = {}

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
        json_output = json_content.get("output")

        if "user" in json_output:
            self.bionano_user_dict = json_output.get("user")
        if "token" in json_output:
            self.bionano_token = json_output.get("token")

        return json_content

    def _get_auth_cookies(self) -> Dict[str, str]:
        """Parse and set authentication cookies based on a prepopulated values of token etc.
        Called after self._get_token, by methods that need cookies for accessing bionano-access.
        Note that the cookie names expected by subsequent calls are not exactly the names in the user dict returned
        by the
        auth request.

        Returns:
            cookies(dict): "token", "email", "fullname", "userpk", "userrole"
        """
        cookies = {
            "token": self.bionano_token,
            "email": self.bionano_user_dict.get("email"),
            "fullname": self.bionano_user_dict.get("full_name"),
            "userpk": call_safe(str, self.bionano_user_dict.get("userpk")),
            "userrole": call_safe(str, self.bionano_user_dict.get("role")),
        }
        return cookies

    def _get_json(self, query: str) -> Optional[Iterable]:
        json_response = get_request_json(query, cookies=self._get_auth_cookies())

        json_content = json_response.get("content")
        if not json_content:
            return None

        return json_content

    def _get_projects(self) -> Optional[List[Dict[str, str]]]:
        """Get a list of projects for the current bionano-access user."""
        projects = []
        query = f"{self.url}/Bnx/api/2.0/getProjects"

        projects = self._get_json(query)

        return projects

    def _get_samples(self, project_uid: str) -> Optional[List[Dict[str, str]]]:
        """Get a list of samples for a given project uid."""
        samples = []
        query = f"{self.url}/Bnx/api/2.0/getSamples?projectuid={project_uid}"

        samples = self._get_json(query)

        return samples

    def _get_uids_from_names(
        self, project_name: str, sample_name: str
    ) -> Optional[Tuple[str, str]]:
        """Get server UIDs given project name and sample name."""
        projects = self._get_projects()
        if not projects:
            raise ValueError()

        for project in projects:
            if project_name in project.get("name"):
                project_uid = project.get("projectuid")
                break

        samples = self._get_samples(project_uid)
        if not samples:
            raise ValueError()

        for sample in samples:
            if sample_name in sample.get("samplename"):
                sample_uid = sample.get("sampleuid")
                break
        return (project_uid, sample_uid)

    def _get_fshd_reports(
        self, project_uid: str, sample_uid: str
    ) -> Optional[List[Dict[str, str]]]:
        """Get FSHD report if available for the given project and sample."""
        query = (
            f"{self.url}/Bnx/api/2.0/getFSHDReport?projectuid={project_uid}&sampleuid={sample_uid}"
        )

        reports = self._get_json(query)

        return reports

    def _parse_fshd_report(self, report: Dict[str, str]) -> Optional[List[Dict[str, str]]]:
        """Parse BioNano FSHD report.
        Accepts a JSON iterable and returns an iterable with d4z4 loci dicts to display.

        The FSHD report locus section contains a set of values that we want to parse out and store with case display
        friendly key names.
        """
        FSHD_D4Z4_LOCUS_KEY_MAPPING = {
            "map_id": "MapID",
            "chromosome": "Chr",
            "haplotype": "Haplotype",
            "count": "Count_repeat",
            "spanning_coverage": "Repeat_spanning_coverage",
        }

        detailed_results = report.get("Detailed results")
        if not detailed_results:
            LOG.warning("No detailed FSHD results found.")
            return None

        fshd_loci = []
        for result in detailed_results.get("value"):
            d4z4 = {}
            for d4z4_key in FSHD_D4Z4_LOCUS_KEY_MAPPING.keys():
                d4z4[d4z4_key] = result[FSHD_D4Z4_LOCUS_KEY_MAPPING[d4z4_key]]["value"]
            fshd_loci.append(d4z4)

        return fshd_loci

    def get_fshd_report(
        self, project_name: str, sample_name: str
    ) -> Optional[List[Dict[str, str]]]:
        """Retrieve FSHD report from a configured bionano access server.
        Accepts a project name and a sample name, and returns an iterable with d4z4 loci dicts to display.

        Returns None if access failed.
        """
        try:
            (project_uid, sample_uid) = self._get_uids_from_names(project_name, sample_name)
        except ValueError:
            return None

        if not project_uid:
            return None

        reports = self._get_fshd_reports(project_uid, sample_uid)
        if not reports:
            flash(NO_BIONANO_FSHD_REPORT_FLASH_MESSAGE, "error")
            return None

        for report in reports:
            if not report.get("job"):
                continue

            report_sample_uid_dict = report.get("job").get("value").get("sampleuid")
            report_sample_uid = report_sample_uid_dict.get("value")
            if report_sample_uid == sample_uid:
                return self._parse_fshd_report(report)

        flash(NO_BIONANO_FSHD_REPORT_FLASH_MESSAGE, "error")
