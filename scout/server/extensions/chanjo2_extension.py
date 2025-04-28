import logging
from typing import Dict

import requests
from flask import Flask, current_app

from scout.server.utils import get_case_mito_chromosome
from scout.utils.scout_requests import get_request_json, post_request_json

REF_CHROM = "14"
LOG = logging.getLogger(__name__)

CHANJO_BUILD_37 = "GRCh37"
CHANJO_BUILD_38 = "GRCh38"


class Chanjo2Client:
    """Runs requests to chanjo2 and returns results in the expected format."""

    def init_app(self, app: Flask):
        """The chanjo2 client has nothing to init, just check chanjo2 heartbeat."""
        self.get_status(app)

    def get_status(self, app: Flask) -> dict:
        """Check Chanjo2 heartbeat, LOG status and return status."""
        chanjo2_heartbeat_url: str = app.config.get("CHANJO2_URL")
        json_resp = get_request_json(chanjo2_heartbeat_url)

        if not json_resp:
            LOG.warning(
                f"Chanjo2 is configured at {chanjo2_heartbeat_url} but does not return heartbeat."
            )
            return json_resp

        LOG.info(f"{json_resp.get('content',{}).get('message')}")
        return json_resp

    def mt_coverage_stats(self, case_obj: dict) -> Dict[str, dict]:
        """Sends a POST requests to the chanjo2 coverage/d4/interval to collect stats for the MT case report."""

        chanjo2_chrom_cov_url: str = "/".join(
            [current_app.config.get("CHANJO2_URL"), "coverage/d4/interval/"]
        )
        coverage_stats = {}
        case_mt_chrom = get_case_mito_chromosome(case_obj)
        for ind in case_obj.get("individuals", []):

            if not ind.get("d4_file"):
                continue
            chrom_cov_query = {"coverage_file_path": ind["d4_file"]}

            # Get mean coverage over chr14
            chrom_cov_query["chromosome"] = REF_CHROM

            autosome_cov_json = post_request_json(chanjo2_chrom_cov_url, chrom_cov_query)
            if autosome_cov_json.get("status_code") != 200:
                raise ValueError(
                    f"Chanjo2 get autosome coverage failed: {autosome_cov_json.get('message')}"
                )

            autosome_cov = autosome_cov_json.get("content", {}).get("mean_coverage")

            # Get mean coverage over chrMT
            chrom_cov_query["chromosome"] = case_mt_chrom
            mt_cov_json = post_request_json(chanjo2_chrom_cov_url, chrom_cov_query)
            if mt_cov_json.get("status_code") != 200:
                raise ValueError(f"Chanjo2 get MT coverage failed: {mt_cov_json.get('message')}")
            mt_cov = mt_cov_json.get("content", {}).get("mean_coverage")

            coverage_info = dict(
                mt_coverage=mt_cov,
                autosome_cov=autosome_cov,
                mt_copy_number=round((mt_cov / autosome_cov) * 2, 2),
            )
            coverage_stats[ind["individual_id"]] = coverage_info

        return coverage_stats

    def get_gene_complete_coverage(
        self, hgnc_id: int, threshold: int = 15, individuals: dict = {}, build: str = "38"
    ) -> bool:
        """
        Return complete coverage for hgnc_id at a coverage threshold.
        """
        chanjo_build = CHANJO_BUILD_37 if "37" in build else CHANJO_BUILD_38
        chanjo2_gene_cov_url: str = "/".join(
            [current_app.config.get("CHANJO2_URL"), "coverage/d4/genes/summary"]
        )

        gene_cov_query = {
            "build": chanjo_build,
            "coverage_threshold": threshold,
            "hgnc_gene_ids": [hgnc_id],
            "interval_type": "genes",
            "samples": [],
        }
        analysis_types = []

        for ind in individuals:
            if not ind.get("d4_file"):
                continue

            gene_cov_query["samples"].append(
                {"coverage_file_path": ind["d4_file"], "name": ind["individual_id"]}
            )
            analysis_types.append(ind.get("analysis_type"))

        if "wes" in analysis_types:
            gene_cov_query["interval_type"] = "exons"
        elif "wts" in analysis_types:
            gene_cov_query["interval_type"] = "transcripts"

        gene_cov_json = post_request_json(chanjo2_gene_cov_url, gene_cov_query)

        if gene_cov_json.get("status_code") != 200:
            raise ValueError(
                f"Chanjo2 get complete coverage failed: {gene_cov_json.get('message')}"
            )

        gene_cov = gene_cov_json.get("content")
        full_coverage = bool(gene_cov)
        for sample in gene_cov.keys():
            if gene_cov[sample]["coverage_completeness_percent"] < 100:
                full_coverage = False

        return full_coverage
