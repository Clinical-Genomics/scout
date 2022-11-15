import logging

import requests

LOG = logging.getLogger(__name__)
SERVICE_URL = "http://127.0.0.1:8000/"


class ClinVarApi:
    """This class contains the code to covert CSV-based ClinVar submissions to json data
    using the preClinVar service: https://preclinvar-stage.scilifelab.se/docs. Json data is validated against
    the ClinVar submission schema (https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/) and if valid, can be directly submitted to ClinVar.
    """

    def __init__(self):
        self.service = SERVICE_URL

    def convert_to_json(self, variant_file, casedata_file):
        """Sends a POST request to the API (csv_2_json endpoint) and tries to convert Variant and Casedata csv files to a JSON submission object(dict)

        Args:
            variant_file(tempfile._TemporaryFileWrapper): a tempfile containing Variant data
            casedata_file(tempfile._TemporaryFileWrapper): a tempfile containing CaseData data

        Returns:
            resp_res(tuple): example -> 400, "Created json file contains validation errors"
                                     -> 200, {dict representation of the submission}
        """
        url = "".join([SERVICE_URL, "csv_2_json"])
        files = [
            ("files", (variant_file, open(variant_file, "r"))),
            ("files", (casedata_file, open(casedata_file, "r"))),
        ]
        try:
            resp = requests.post(url, files=files)
            LOG.error(str(resp.json()))
            return resp.status_code, resp
        except Exception as ex:
            return None, ex
