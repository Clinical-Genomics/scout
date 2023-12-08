import logging
from typing import Callable, Dict, Iterator

import requests
from schug.load.biomart import EnsemblBiomartClient
from schug.load.ensembl import fetch_ensembl_exons, fetch_ensembl_genes, fetch_ensembl_transcripts
from schug.models.common import Build as SchugBuild

LOG = logging.getLogger(__name__)

BUILDS: Dict[str, str] = {"37": "GRCh37", "38": "GRCh38"}

ENSEMBL_RESOURCE_CLIENT: Dict[str, Callable] = {
    "genes": fetch_ensembl_genes,
    "transcripts": fetch_ensembl_transcripts,
    "exons": fetch_ensembl_exons,
}


class EnsemblBiomartHandler:
    """A class that handles Ensembl genes, transcripts and exons downloads via schug."""

    def __init__(self, build: str = "37"):
        self.build: str = BUILDS[build]

    def biomart_get(self, url: str) -> Iterator:
        """Sends a request to Ensembl Biomart and returns the resource lines."""
        response: requests.models.responses = requests.get(url, stream=True)
        return response.iter_lines(decode_unicode=True)

    def stream_resource(self, interval_type: str) -> Iterator[str]:
        """Fetches genes, transcripts or exons from a remote Ensembl biomart in the right genome build and saves them to file."""

        def yield_resource_lines(iterable) -> str:
            """Removes the last element from an iterator."""
            it = iter(iterable)
            current = next(it)
            for i in it:
                yield current
                current = i

        shug_client: EnsemblBiomartClient = ENSEMBL_RESOURCE_CLIENT[interval_type](
            build=SchugBuild(self.build)
        )

        url: str = shug_client.build_url(xml=shug_client.xml)

        # return all lines except the last, which contains the "[success]" string
        return yield_resource_lines(self.biomart_get(url))
