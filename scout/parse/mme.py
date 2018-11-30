# -*- coding: utf-8 -*-
import logging
from scout.resources import mme_schema_path

LOG = logging.getLogger(__name__)

def validate_mme_json(json_file):
    """Validate a json file containing matchmaker exchange json patients against
    the json schema defined in https://github.com/ga4gh/mme-apis

    Args:
        json_file(str): path to json file containing one or more patients

    Returns
        valid_json(bool): True if file passed validation, otherwise False

    """
    LOG.info('Validation json schema for MME patients from file {}'.format(json_file))

    mme_api_schema = mme_schema_path
    return mme_schema
