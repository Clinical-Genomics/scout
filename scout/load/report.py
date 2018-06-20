import logging
import pymongo

from scout.exceptions import (IntegrityError, ValidationError)

LOG = logging.getLogger(__name__)

def load_report(adapter, case_id, report_path, update=False):
    """Add the path to a report to a case
    
    Args:
        adapter(scout.adapter.MongoAdapter)
        case_id(str)
        report_path(str)
        update(bool)
    
    Returns:
        updated_case(dict)
    """
    case_obj = adapter.case(case_id)
    if not case_obj:
        raise IntegrityError("Case {0} does not exist".format(case_id))
    if case_obj.get('delivery_report'):
        if not update:
            raise ValidationError("Delivery report already exists for case {}".format(case_id))
    
    LOG.info("Set delivery report to %s", report_path)    
    updated_case = adapter.case_collection.find_one_and_update({'_id': case_id}, 
                            {'$set': {'delivery_report':report_path}},
                            return_document = pymongo.ReturnDocument.AFTER
                            )
    
    return updated_case
