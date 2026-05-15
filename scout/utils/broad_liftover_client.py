import logging
from typing import Optional, Tuple

import requests
from flask import flash

LOG = logging.getLogger(__name__)

HEADERS = {"Content-type": "application/json"}
LIFTOVER_URL = "https://liftover-xwkwwwxdwq-uc.a.run.app/liftover/"


class BroadLiftoverApiClient:
    """A class handling requests and responses to and from the Broad institute liftover API.
    Endpoint: https://liftover-xwkwwwxdwq-uc.a.run.app/liftover/docs/
    """

    def __init__(self):
        self.server = LIFTOVER_URL

    @staticmethod
    def send_request(url) -> Optional[dict]:
        """Sends the actual request to the server and returns the response."""
        error = None
        data = None
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code not in [404, 500]:

                data = response.json()
            else:
                error = f"Ensembl request failed with code:{response.status_code} for url {url}"
        except requests.exceptions.HTTPError:
            error = f"Ensembl request failed with HTTPError error for url {url}"

        if error:
            flash(error)
        return data

    def set_request_build_params(self, build_from_raw: str) -> Tuple[str, str]:
        """Set build_from and build_to given the params passed to the function."""

        if "38" in build_from_raw:
            build_from = "hg38"
            build_to = "hg19"
        else:
            build_from = "hg19"
            build_to = "hg38"

        return build_from, build_to

    def liftover(
        self,
        build_from: str,
        chrom: str,
        start: int,
        end: Optional[int] = None,
        ref: Optional[str] = None,
        alt: Optional[str] = None,
    ) -> Optional[dict]:
        """Perform variant liftover using the API with BCFtools plugin or the UCSC liftover tool, if alt and ref are missing.
        example:  https://liftover-xwkwwwxdwq-uc.a.run.app/liftover/?hg=hg19-to-hg38&format=variant&chrom=11&pos=47353394&end=47353394&ref=T&alt=C
        """

        build_from, build_to = self.set_request_build_params(build_from)

        if alt and ref:  # use BCFtools plugin
            req_format = "variant"
            start_param = "pos"
        else:  # use UCSC tool
            req_format = "interval"
            start_param = "start"

        url = f"{LIFTOVER_URL}/?hg={build_from}-to-{build_to}&format={req_format}&chrom={chrom}&{start_param}={start}"

        if end:
            url += f"&end={end}"
        if ref:
            url += f"&ref={ref}"
        if alt:
            url += f"&alt={alt}"

        result = self.send_request(url)
        if isinstance(result, dict):
            return result

    def __repr__(self):
        return f"BroadLiftoverApiClient:server:{self.server}"
