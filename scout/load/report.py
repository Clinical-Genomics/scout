# -*- coding: utf-8 -*-
import logging

from scout.adapter import MongoAdapter
from scout.exceptions import IntegrityError, DataNotFoundError

LOG = logging.getLogger(__name__)


def load_delivery_report(
    adapter: MongoAdapter, report_path: str, case_id: str, update: bool = False
):
    """Load a delivery report into a case in the database

    If the report already exists the function will exit.
    If the user want to load a report that is already in the database
    'update' has to be 'True'

    Args:
        adapter     (MongoAdapter): Connection to the database
        report_path (string):       Path to delivery report
        case_id     (string):       Optional case identifier
        update      (bool):         If an existing report should be replaced

    Returns:
        updated_case(dict)

    """

    case_obj = adapter.case(case_id=case_id)

    if case_obj is None:
        raise DataNotFoundError("no case found")

    if update or case_obj.get("delivery_report") is None:
        _update_report_path(case_obj, report_path, "delivery_report")
    else:
        raise IntegrityError("Existing report found, use update = True to " "overwrite")

    LOG.info("Saving report for case {} in database".format(case_obj["_id"]))
    return adapter.replace_case(case_obj)


def load_cnv_report(adapter: MongoAdapter, report_path: str, case_id: str, update: bool = False):
    """Load a CNV report into a case in the database

    If the report already exists the function will exit.
    If the user want to load a report that is already in the database
    'update' has to be 'True'

    Args:
        adapter     (MongoAdapter): Connection to the database
        report_path (string):       Path to CNV report
        case_id     (string):       Optional case identifier
        update      (bool):         If an existing report should be replaced

    Returns:
        updated_case(dict)

    """

    case_obj = adapter.case(case_id=case_id)

    if case_obj is None:
        raise DataNotFoundError("no case found")

    if update or case_obj.get("cnv_report") is None:
        _update_report_path(case_obj, report_path, "cnv_report")
    else:
        raise IntegrityError("Existing report found, use update = True to " "overwrite")

    LOG.info("Saving report for case {} in database".format(case_obj["_id"]))
    return adapter.replace_case(case_obj)


def load_coverage_qc_report(
    adapter: MongoAdapter, report_path: str, case_id: str, update: bool = False
):
    """Load a coverage and qc report into a case in the database

    If the report already exists the function will exit.
    If the user want to load a report that is already in the database
    'update' has to be 'True'

    Args:
        adapter     (MongoAdapter): Connection to the database
        report_path (string):       Path to coverage and qc report
        case_id     (string):       Optional case identifier
        update      (bool):         If an existing report should be replaced

    Returns:
        updated_case(dict)

    """

    case_obj = adapter.case(case_id=case_id)

    if case_obj is None:
        raise DataNotFoundError("no case found")

    if update or case_obj.get("coverage_qc_report") is None:
        _update_report_path(case_obj, report_path, "coverage_qc_report")
    else:
        raise IntegrityError("Existing report found, use update = True to " "overwrite")

    LOG.info("Saving report for case {} in database".format(case_obj["_id"]))
    return adapter.replace_case(case_obj)


def _update_report_path(case_obj, report_path, report_type):
    """Updates the report path

    Args:
        case_obj     (Case):         Case object
        report_path  (string):       Path to CNV report
        report_type  (string):       Type of report
    """
    case_obj[report_type] = report_path
    return True
