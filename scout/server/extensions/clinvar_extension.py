import json
import logging
from io import StringIO
from typing import Optional, Tuple

import requests
from flask import flash

from scout.constants.clinvar import CLINVAR_API_URL_DEFAULT, PRECLINVAR_URL

LOG = logging.getLogger(__name__)


class ClinVarApi:
    """This class contains the code to covert CSV-based ClinVar submissions to json data
    using the preClinVar service: https://preclinvar-stage.scilifelab.se/docs. Json data is validated against
    the ClinVar submission schema (https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/) and if valid, can be directly submitted to ClinVar.
    """

    def init_app(self, app):
        self.convert_service = "/".join([PRECLINVAR_URL, "csv_2_json"])
        self.delete_service = "/".join([PRECLINVAR_URL, "delete"])
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

    def convert_to_json(self, variant_file, casedata_file, extra_params={}):
        """Sends a POST request to the API (tsv_2_json endpoint) and tries to convert Variant and Casedata csv files to a JSON submission object(dict)

        Args:
            variant_file(tempfile._TemporaryFileWrapper): a tempfile containing Variant data
            casedata_file(tempfile._TemporaryFileWrapper): a tempfile containing CaseData data
            extra_params(dict): a dictionary containing key/values to be sent as extra params to the csv_2_json endpoint (assertion criteria, genome assembly etc)

        Returns:
            tuple: example -> 400, "Created json file contains validation errors"
                           -> 200, {dict representation of the submission}
        """
        files = [
            ("files", (variant_file, open(variant_file, "r"))),
            ("files", (casedata_file, open(casedata_file, "r"))),
        ]
        try:
            resp = requests.post(self.convert_service, params=extra_params, files=files)
            return resp.status_code, resp.json()
        except Exception as ex:
            return None, ex

    def submit_json(self, json_data, api_key=None):
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

    def json_submission_status(self, submission_id: str, api_key=None) -> dict:
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

    def delete_clinvar_submission(self, submission_id: str, api_key=None) -> Tuple[int, dict]:
        """Remove a successfully processed submission from ClinVar."""

        try:
            submission_status_doc: dict = self.json_submission_status(
                submission_id=submission_id, api_key=api_key
            )

            subm_response: dict = submission_status_doc["actions"][0]["responses"][0]
            submission_status = subm_response["status"]

            if submission_status != "processed":
                return (
                    500,
                    f"Clinvar submission status should be 'processed' and in order to attempt data deletion. Submission status is '{submission_status}'.",
                )

            # retrieve ClinVar SCV accession (SCVxxxxxxxx) from file url returned by subm_response
            subm_summary_url: str = subm_response["files"][0]["url"]
            scv_accession: Optional(str) = self.get_clinvar_scv_accession(url=subm_summary_url)

            # Remove ClinVar submission using preClinVar's 'delete' endpoint
            resp = requests.post(
                self.delete_service, data={"api_key": api_key, "clinvar_accession": scv_accession}
            )
            return resp.status_code, resp.json()

        except Exception as ex:
            return 500, str(ex)
