import logging

import requests

from scout.utils.scout_requests import get_request_json

LOG = logging.getLogger(__name__)
NORMALIZE_API = "https://mutalyzer.nl/api"


class MutalyzerClient:
    """A proxy class to handle requests to the Mutalyzer 3 service API (https://mutalyzer.nl/api/).
    Mutalyzer check descriptions of sequence variants according to the Human Genome Sequence Variation Society (HGVS) guidelines."""

    def normalized_description(self, refseq, hgvs, build):
        """Normalize a variant description using the Mutalyzer normalizer tool

        Args:
            refseq(str): example -> NM_001410
            hgvs(str): example -> c.510G>T
            build(str): "37" or "38"

        Returns:
            a normalized hgvs description (str) in the requested genome build
        """
        normalize_url = f"{NORMALIZE_API}/normalize/{refseq}:{hgvs}?only_variants=false"
        resp = get_request_json(normalize_url)

        for desc in resp.get("chromosomal_descriptions", []):
            if build not in desc["assembly"]:
                continue
            return desc["description"]
