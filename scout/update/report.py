# -*- coding: utf-8 -*-
import logging
from typing import Optional

from scout.constants import CUSTOM_CASE_REPORTS
from scout.exceptions import DataNotFoundError
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def update_case_report(
    case_id: str, report_path: str, report_key: str, delete: Optional[bool] = False
) -> dict:
    """Update a report document for a case.
    Updates any key from CUSTOM_CASE_REPORTS with a report path on disk.
    If delete is true, the key is instead popped from the case.
    Returns the updated case.
    """
    case_obj = store.case(case_id=case_id)
    if case_obj is None:
        raise DataNotFoundError(f"No case with _id {case_id} found")
    report_key = CUSTOM_CASE_REPORTS[report_key]["key_name"]
    if delete:
        case_obj.pop(report_key, None)
    else:
        case_obj[report_key] = report_path
    return store.replace_case(case_obj)
