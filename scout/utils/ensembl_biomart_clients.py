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

        shug_url: str = f"{SCHUG_BASE}{SCHUG_RESOURCE_URL[interval_type]}{self.build}"

        return self.stream_get(shug_url)

    def check_integrity(self, file_path: str):
        """Counts the number of lines containing '[success]'. One such line per chromosome is expected for the file to be considered intact."""

        def count_line_occurrences(file_path, target_line):
            with open(file_path, "r", encoding="utf-8") as file:
                return sum(1 for line in file if line.strip() == target_line)

        nr_chromosomes_in_file = count_line_occurrences(file_path, "[success]")
        nr_chromosomes = 24
        if nr_chromosomes_in_file < nr_chromosomes:
            raise BufferError(
                f"Ensembl resource {file_path} does not seem to be complete. Please retry downloading the file."
            )

        LOG.info("Integrity check OK")
