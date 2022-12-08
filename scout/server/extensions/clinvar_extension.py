import json
import logging
from tempfile import NamedTemporaryFile

import requests

LOG = logging.getLogger(__name__)

SERVICE_URL = "https://preclinvar-stage.scilifelab.se"


class ClinVarApi:
    """This class contains the code to covert CSV-based ClinVar submissions to json data
    using the preClinVar service: https://preclinvar-stage.scilifelab.se/docs. Json data is validated against
    the ClinVar submission schema (https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/) and if valid, can be directly submitted to ClinVar.
    """

    def __init__(self):
        self.convert_service = "/".join([SERVICE_URL, "csv_2_json"])
        self.validate_service = "/".join([SERVICE_URL, "validate"])

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
            return resp.status_code, resp
        except Exception as ex:
            return None, ex

    def validate_json(self, subm_data, api_key):
        """Sends a POST request to the API (validate endpoint) and tries to validate a json submission object.
        Requires a valid ClinVar API key (obtained from scout config file in order to be able to forward the request)

        Args:
            subm_data(dict): the json-like ClinVar submission object to be validated
            api_key: A ClinVar submission API key (https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/)

        Returns:
            tuple: example -> 400, "{Validation errors}"
                           -> 201, {"id": "SUB12387166"} # Success is 201 - Created - According to the ClinVar API
        """
        try:
            tmp = NamedTemporaryFile(prefix="submission", suffix=".json")

            # write data to file
            with open(tmp.name, "w") as f:
                json.dump(subm_data, f)

            with open(tmp.name) as f:  # read from file
                json_file = {"json_file": open(f.name, "rb")}
                resp = requests.post(
                    self.validate_service, data={"api_key": api_key}, files=json_file
                )
                return resp.status_code, resp

        except Exception as ex:
            return None, ex
