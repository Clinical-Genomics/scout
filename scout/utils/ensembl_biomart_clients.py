import logging
import os
import shutil
from typing import Callable, Dict

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

    def download_resource(self, interval_type: str, save_path: str) -> None:
        """Fetches genes, transcripts or exons from a remote Ensembl biomart in the right genome build and saves them to file."""

        shug_client: EnsemblBiomartClient = ENSEMBL_RESOURCE_CLIENT[interval_type](
            build=SchugBuild(self.build)
        )
        url: str = shug_client.build_url(xml=shug_client.xml)

        with requests.get(url, stream=True) as r:
            with open(save_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)

        # Remove the last line of the file, which contains the string `[success]`
        with open(save_path, "r+") as f:
            current_position = previous_position = f.tell()
            while f.readline():
                previous_position = current_position
                current_position = f.tell()
            f.truncate(previous_position)
