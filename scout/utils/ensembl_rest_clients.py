"""Code for talking to ensembl rest API"""

import logging
from typing import Optional
from urllib.parse import urlencode

import requests
from flask import flash

LOG = logging.getLogger(__name__)

HEADERS = {"Content-type": "application/json"}
RESTAPI_37 = "https://grch37.rest.ensembl.org"
RESTAPI_38 = "https://rest.ensembl.org"
WARNING = "warning"


class EnsemblRestApiClient:
    """A class handling requests and responses to and from the Ensembl REST APIs.
    Endpoints for human build 37: https://grch37.rest.ensembl.org
    Endpoints for human build 38: http://rest.ensembl.org/
    Documentation: https://github.com/Ensembl/ensembl-rest/wiki
    doi:10.1093/bioinformatics/btu613
    """

    def __init__(self, build="37"):
        if build == "38":
            self.server = RESTAPI_38
        else:
            self.server = RESTAPI_37

    def build_url(self, endpoint, params=None):
        """Build an url to query ensembml"""
        if params:
            endpoint += "?" + urlencode(params)

        return "".join([self.server, endpoint])

    @staticmethod
    def send_request(url) -> Optional[dict]:
        """Sends the actual request to the server and returns the response

        Accepts:
            url(str): ex. https://rest.ensembl.org/overlap/id/ENSG00000157764?feature=transcript

        Returns:
            data(dict): dictionary from json response
        """
        error = None
        data = None
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code not in [404, 500]:

                data = response.json()
            else:
                error = f"Ensembl request failed with code:{response.status_code} for url {url}"
        except requests.exceptions.MissingSchema as err:
            error = f"Ensembl request failed with MissingSchema error for url {url}"
        except requests.exceptions.HTTPError as err:
            error = f"Ensembl request failed with HTTPError error for url {url}"

        if error:
            flash(error, WARNING)
        return data

    def liftover(self, build, chrom, start, end=None):
        """Perform variant liftover using Ensembl REST API

        Args:
            build(str): genome build: "37" or "38"
            chrom(str): 1-22,X,Y,MT,M
            start(int): start coordinate
            stop(int): stop coordinate or None

        Returns:
            mappings(list of dict): example:
                example: https://rest.ensembl.org/map/human/GRCh37/X:1000000..1000100:1/GRCh38?content-type=application/json
        """

        build = "GRCh38" if "38" in str(build) else "GRCh37"
        assembly2 = "GRCh38" if build == "GRCh37" else "GRCh37"

        url = "/".join(
            [
                self.server,
                "map/human",
                build,
                f"{chrom}:{start}..{end or start}",  # End variant provided is not required
                f"{assembly2}?content-type=application/json",
            ]
        )
        result = self.send_request(url)
        if isinstance(result, dict):
            return result.get("mappings")

    def __repr__(self):
        return f"EnsemblRestApiClient:server:{self.server}"
