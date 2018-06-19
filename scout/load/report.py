# -*- coding: utf-8 -*-
import logging
from dateutil.parser import parse as parse_date

from mongo_adapter import MongoAdapter
from scout.exceptions import IntegrityError, DataNotFoundError

logger = logging.getLogger(__name__)


def load_delivery_report(adapter: MongoAdapter,
                         report_path: str,
                         analysis_date: str = None,
                         case_id: str = None,
                         institute_id: str = None,
                         display_name: str = None,
                         update: bool = False):
    """Load a delivery report into the database

    If the report already exists the function will exit.
    If the user want to load a report that is already in the database
    'update' has to be 'True'

    Args:
        :param adapter: (MongoAdapter) connection to the database
        :param analysis_date: (string) optional date of analysis that the report belongs to
        :param report_path: (string) path to report
        :param institute_id: (string) customer id, optional when using case_id
        :param case_id: (string) optional case identifier
        :param display_name: (string) displayed case id, optional when using case_id
        :param update: (bool) If existing report should be updated
    Returns:
        None

    """

    case_obj = adapter.case(
        case_id=case_id,
        institute_id=institute_id,
        display_name=display_name
    )

    if case_obj is None:
        raise DataNotFoundError("no case found")

    if analysis_date:
        delivery_report_added = put_report_in_analyses_list(analysis_date, case_obj, report_path,
                                                            update)
    else:
        delivery_report_added = put_report_in_case_root(case_obj, report_path)

    if not delivery_report_added:
        raise DataNotFoundError('Could not add the delivery report for unknown reasons')

    logger.info('Saving report for case {} in database'.format(case_obj['_id']))
    return adapter.replace_case(case_obj)


def put_report_in_analyses_list(analysis_date, case_obj, report_path, update):
    analysis_date = parse_date(analysis_date)

    has_existing_analyses_list = case_obj.get('analyses')

    if has_existing_analyses_list:
        delivery_report_added = put_delivery_report_in_existing_analyses_list(analysis_date,
                                                                              case_obj,
                                                                              report_path, update)
    else:
        delivery_report_added = put_delivery_report_in_new_analyses_list(analysis_date, case_obj,
                                                                         report_path)
    return delivery_report_added


def put_delivery_report_in_new_analyses_list(analysis_date, case_obj,
                                             report_path):
    case_obj['analyses'] = [{'date': analysis_date, 'delivery_report': report_path}]
    return True


def put_delivery_report_in_existing_analyses_list(analysis_date, case_obj,
                                                  report_path, update):
    delivery_report_added = False
    for analysis_data in case_obj['analyses']:
        if analysis_data['date'] == analysis_date:
            if update:
                delivery_report_added = put_delivery_report_in_existing_analyses_item(analysis_data,
                                                                                      report_path)
            else:
                raise IntegrityError('Existing delivery report found, use update = True to '
                                     'overwrite')

    if not delivery_report_added:
        delivery_report_added = put_delivery_report_last_in_analyses_list(analysis_date, case_obj,
                                                                          report_path)
    return delivery_report_added


def put_delivery_report_in_existing_analyses_item(analysis_data,
                                                  report_path):
    analysis_data['delivery_report'] = report_path
    return True


def put_delivery_report_last_in_analyses_list(analysis_date, case_obj,
                                              report_path):
    case_obj['analyses'].append({'date': analysis_date, 'delivery_report':
        report_path})
    return True


def put_report_in_case_root(case_obj, report_path):
    case_obj['delivery_report'] = report_path
    return True
