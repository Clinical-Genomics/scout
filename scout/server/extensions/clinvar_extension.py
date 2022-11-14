import requests

SERVICE_URL = "https://preclinvar-stage.scilifelab.se/"


class ClinVarApi:
    """This class contains the code to covert CSV-based ClinVar submissions to json data
    using the preClinVar service: https://preclinvar-stage.scilifelab.se/docs. Json data is validated against
    the ClinVar submission schema (https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/) and if valid, can be directly submitted to ClinVar.
    """

    def __init__(self):
        self.service = SERVICE_URL

    def convert_to_json(self, variant_file, casedata_file):
        """Sends a POST request to the API and tries to convert Variant and Casedata csv files to a JSON submission object(dict)

        Args:
            variant_file(tempfile._TemporaryFileWrapper): a tempfile containing Variant data
            casedata_file(tempfile._TemporaryFileWrapper): a tempfile containing CaseData data

        Returns:
            resp_res(tuple): example -> 400, "Created json file contains validation errors"
                                     -> 200, dict representing the submission object
        """
        url = "".join([SERVICE_URL, "csv_2_json"])
        files = [
            ("files", (variant_file, open(variant_file, "r"))),
            ("files", (casedata_file, open(casedata_file, "r"))),
        ]
        try:
            resp = requests.post(url, files=files)
            return resp.status_code, resp.json()
        except Exception as ex:
            return None, ex
