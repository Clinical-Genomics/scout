# -*- coding: utf-8 -*-
import logging

from mongo_adapter import MongoAdapter
from scout.exceptions import IntegrityError, DataNotFoundError

logger = logging.getLogger(__name__)


def load_delivery_report(adapter: MongoAdapter,
                         report_path: str,
                         case_id: str,
                         update: bool = False):
    """Load a delivery report into the database

    If the report already exists the function will exit.
    If the user want to load a report that is already in the database
    'update' has to be 'True'

    Args:
        :param adapter: (MongoAdapter) connection to the database
        leave empty for latest
        :param report_path: (string) path to report
        :param case_id: (string) optional case identifier
        :param update: (bool) If existing report should be updated
    Returns:
        None

    """

    case_obj = adapter.case(
        case_id=case_id,
    )

    if case_obj is None:
        raise DataNotFoundError("no case found")

    print('asdf', case_obj.get('delivery_report'), update)

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
