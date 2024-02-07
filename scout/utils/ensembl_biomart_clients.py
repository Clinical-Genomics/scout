import logging
from typing import Dict, Iterator

import requests

LOG = logging.getLogger(__name__)
SCHUG_BASE = "https://schug.scilifelab.se"

BUILDS: Dict[str, str] = {"37": "GRCh37", "38": "GRCh38"}

SCHUG_RESOURCE_URL: Dict[str, str] = {
    "genes": "/genes/ensembl_genes/?build=",
    "transcripts": "/transcripts/ensembl_transcripts/?build=",
    "exons": "/exons/ensembl_exons/?build=",
}


class EnsemblBiomartHandler:
    """A class that handles Ensembl genes, transcripts and exons downloads via schug-web."""

    def __init__(self, build: str = "37"):
        self.build: str = BUILDS[build]

    def stream_get(self, url: str) -> Iterator:
        """Sends a request to Schug web and returns the resource lines."""
        response: requests.models.responses = requests.get(url, stream=True)
        return response.iter_lines(decode_unicode=True)

    def stream_resource(self, interval_type: str) -> Iterator[str]:
        """Use schug web to fetch genes, transcripts or exons from a remote Ensembl biomart in the right genome build and save them to file."""

        def yield_resource_lines(iterable) -> str:
            """Removes the last element from an iterator."""
            it = iter(iterable)
            current = next(it)
            for i in it:
                yield current
                current = i

        shug_url: str = f"{SCHUG_BASE}{SCHUG_RESOURCE_URL[interval_type]}{self.build}"

        # return all lines except the last, which contains the "[success]" string
        return yield_resource_lines(self.stream_get(shug_url))
