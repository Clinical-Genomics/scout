import logging
from typing import Dict

import requests
from flask import current_app

REF_CHROM = "14"
MT_CHROM = "MT"
LOG = logging.getLogger(__name__)


class Chanjo2Client:
    """Runs requests to chanjo2 and returns results in the expected format."""

    def mt_coverage_stats(self, individuals: dict) -> Dict[str, dict]:
        """Sends a POST requests to the chanjo2 coverage/d4/interval to collect stats for the MT case report."""

        chanjo2_chrom_cov_url: str = "/".join(
            [current_app.config.get("CHANJO2_URL"), "coverage/d4/interval/"]
        )
        coverage_stats = {}
        for ind in individuals:

            if not ind.get("d4_file"):
                continue
            chrom_cov_query = {"coverage_file_path": ind["d4_file"]}

            # Get mean coverage over chr14
            chrom_cov_query["chromosome"] = REF_CHROM
            resp = requests.post(chanjo2_chrom_cov_url, json=chrom_cov_query)
            autosome_cov = resp.json().get("mean_coverage")

            # Get mean coverage over chrMT
            chrom_cov_query["chromosome"] = MT_CHROM
            resp = requests.post(chanjo2_chrom_cov_url, json=chrom_cov_query)

            mt_cov = resp.json().get("mean_coverage")

            coverage_info = dict(
                mt_coverage=mt_cov,
                autosome_cov=autosome_cov,
                mt_copy_number=round((mt_cov / autosome_cov) * 2, 2),
            )
            coverage_stats[ind["individual_id"]] = coverage_info

        return coverage_stats
