# -*- coding: utf-8 -*-
import logging

from scout.constants import CUSTOM_CASE_REPORTS
from scout.exceptions import DataNotFoundError
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def update_case_report(case_id, report_path, report_key):
    """Update a report document for a case

    Args:
        case_id(str): _id of a case
        report_path(str): Path to report on disk
        report_key(str): any key from CUSTOM_CASE_REPORTS

    Returns:
        dict: a case dictionary (scout.models.Case)
    """
    case_obj = store.case(case_id=case_id)
    if case_obj is None:
        raise DataNotFoundError(f"No case with _id {case_id} found")
    report_key = CUSTOM_CASE_REPORTS[report_key]["key_name"]
    case_obj[report_key] = report_path
    return store.replace_case(case_obj)
