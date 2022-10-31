# -*- coding: utf-8 -*-
import logging

from scout.exceptions import DataNotFoundError, IntegrityError
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

REPORT_TYPE = {
    "delivery": "delivery_report",
    "cnv": "cnv_report",
    "qc": "coverage_qc_report",
    "qc_rna": "coverage_qc_report_rna",
    "gene_fusion": "gene_fusion_report",
    "gene_fusion_research": "gene_fusion_report_research",
}


def update_case_report(case_id, report_path, report_key):
    """Update a report document for a case

    Args:
        case_id(str): _id of a case
        report_path(str): Path to report on disk
        report_key(str): any key from REPORT_TYPE
    """
    case_obj = store.case(case_id=case_id)
    if case_obj is None:
        raise DataNotFoundError(f"No case with _id {case_id} found")
    LOG.error(f"{REPORT_TYPE[report_key]} - {report_path}")
    case_obj[REPORT_TYPE[report_key]] = report_path
    LOG.error(f"{case_obj['gene_fusion_report_research']}")
    return store.replace_case(case_obj)
