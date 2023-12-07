import logging
from typing import Callable, Dict, Iterator, List

import requests
from schug.load.biomart import EnsemblBiomartClient
from schug.load.ensembl import fetch_ensembl_exons, fetch_ensembl_genes, fetch_ensembl_transcripts
from schug.models.common import Build as SchugBuild

LOG = logging.getLogger(__name__)

BUILD_37 = "GRCh37"
BUILD_38 = "GRCh38"

BUILDS: Dict[str, str] = {
    "37": BUILD_37,
    "38": BUILD_38,
}

ENSEMBL_RESOURCE_CLIENT: Dict[str, Callable] = {
    "genes": fetch_ensembl_genes,
    "transcripts": fetch_ensembl_transcripts,
    "exons": fetch_ensembl_exons,
}


class EnsemblBiomartHandler:
    """A class that handles Ensembl genes, transcripts and exons downloads via schug."""

    def __init__(self, build: str = "37"):
        self.build: str = BUILDS[build]

    def read_resource_lines(self, interval_type: str) -> Iterator[str]:
        """Returns lines of a remote Ensembl Biomart resource (genes, transcripts or exons) in a given genome build."""

        shug_client: EnsemblBiomartClient = ENSEMBL_RESOURCE_CLIENT[interval_type](
            build=SchugBuild(self.build)
        )
        url: str = shug_client.build_url(xml=shug_client.xml)
        response = requests.get(url, stream=True)
        return response.iter_lines(decode_unicode=True)
