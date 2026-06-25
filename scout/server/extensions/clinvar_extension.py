import json
import logging
from io import StringIO
from typing import Any, Optional, Tuple

import requests
from flask import flash

from scout.constants.clinvar import CLINVAR_API_URL_DEFAULT

LOG = logging.getLogger(__name__)


class ClinVarApi:
    """This class contains the code to covert CSV-based ClinVar submissions to json data
    using the preClinVar service: https://preclinvar-stage.scilifelab.se/docs. Json data is validated against
    the ClinVar submission schema (https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/) and if valid, can be directly submitted to ClinVar.
    """

    def init_app(self, app):
        self.submit_service_url = app.config.get("CLINVAR_API_URL") or CLINVAR_API_URL_DEFAULT

    def set_header(self, api_key) -> dict:
        """Creates a header to be submitted a in a POST rquest to the CLinVar API
        Args:
            api_key(str): API key to be used to submit to ClinVar (64 alphanumeric characters)
        Returns:
            header(dict): contains "Content-type: application/json" and "SP-API-KEY: <API-KEY>" key/values
        """
        header = {
            "Content-Type": "application/json",
            "SP-API-KEY": api_key,
        }
        return header

    def submit_json(self, json_data: dict, api_key: Optional[str] = None) -> tuple:
        """Submit a ClinVar submission object using the official ClinVar API

        Args:
            json_data(dict): a json submission object compliant with the ClinVar API
            api_key(str): institute or user-specific ClinVar submission key.
                          Provided by user in ClinVar submission form.

        Returns:
            tuple: example -> 400, "{Validation errors}"
                           -> [201, 200, 204], Response object
        """

        header = self.set_header(api_key)
        data = {
            "actions": [{"type": "AddData", "targetDb": "clinvar", "data": {"content": json_data}}]
        }
        try:
            resp = requests.post(self.submit_service_url, data=json.dumps(data), headers=header)
            return self.submit_service_url, resp.status_code, resp

        except Exception as ex:
            return self.submit_service_url, None, ex

    def json_submission_status(self, submission_id: str, api_key=None) -> Any:
        """Retrieve the status of a ClinVar submission using the https://submit.ncbi.nlm.nih.gov/api/v1/submissions/SUBnnnnnn/actions/ endpoint."""

        header: dict = self.set_header(api_key)
        actions_url = f"{self.submit_service_url}{submission_id}/actions/"
        actions_resp: requests.models.Response = requests.get(actions_url, headers=header)
        return actions_resp.json()

    def get_clinvar_scv_accession(self, url: str) -> Optional[str]:
        """Downloads a submission summary from the given URL into a temporary file and parses this file to retrieve a SCV accession, if available."""
        # Send a GET request to download the file
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed

        # Use an in-memory file-like object to hold the JSON content
        with StringIO(response.text) as memory_file:

            json_data = json.load(memory_file)

            submission_data: dict = json_data["submissions"][0]
            processing_status: str = submission_data["processingStatus"]
            if processing_status != "Success":
                flash(
                    f"Could not delete provided submission because its processing status is '{processing_status}'.",
                    "warning",
                )
                return
            return submission_data["identifiers"]["clinvarAccession"]
