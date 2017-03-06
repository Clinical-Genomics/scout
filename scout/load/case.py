# -*- coding: utf-8 -*-
import logging

from scout.exceptions import IntegrityError
from scout.build.case import build_case

logger = logging.getLogger(__name__)


def load_case(adapter, case_info, update=False):
    """Load a case into the database

    If the case already exists the function will exit.
    If the user want to load a case that is already in the database
    'update' has to be 'True'

    Args:
        adapter (MongoAdapter): connection to the database
        case_info (dict): case object to persist to the database
        update(bool): If existing case should be updated

    Returns:
        case_obj(dict): A dictionary with the builded case
    """
    logger.info('Loading case {} into database'.format(case_info['display_name']))
    case_obj = build_case(case_info, adapter)

    # Check if case exists in database
    existing_case = adapter.case(case_obj['_id'])
    
    if existing_case:
        if update:
            adapter.update_case(case_obj)
        else:
            raise IntegrityError("Case {0} already exists in database".format(
                                 case_obj.case_id))
    else:
        adapter.add_case(case_obj)
    return case_obj
