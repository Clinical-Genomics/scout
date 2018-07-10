# -*- coding: utf-8 -*-
import logging

from scout.adapter import MongoAdapter
from scout.exceptions import IntegrityError, DataNotFoundError

logger = logging.getLogger(__name__)


def load_delivery_report(adapter: MongoAdapter,
                         report_path: str,
                         case_id: str,
                         update: bool = False):
    """ Load a delivery report into a case in the database

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

    case_obj = adapter.case(
        case_id=case_id,
    )

    if case_obj is None:
        raise DataNotFoundError("no case found")

    if not case_obj.get('delivery_report'):
        _put_report_in_case_root(case_obj, report_path)
    else:
        if update:
            _put_report_in_case_root(case_obj, report_path)
        else:
            raise IntegrityError('Existing delivery report found, use update = True to '
                                 'overwrite')

    logger.info('Saving report for case {} in database'.format(case_obj['_id']))
    return adapter.replace_case(case_obj)


def _put_report_in_case_root(case_obj, report_path):
    case_obj['delivery_report'] = report_path
    return True
