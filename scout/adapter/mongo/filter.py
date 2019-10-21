# -*- coding: utf-8 -*-
import logging
from bson.objectid import ObjectId

# needed?
from scout import __version__

import pymongo

LOG = logging.getLogger(__name__)

class FilterHandler(object):
    """Class to handle persistent variant filters in the mongo adapter"""

    def retrieve_filter(self, filter_id):
        """Retrieve a known stored filter object from the db

            Arguments:
                filter_id

            Returns:
                filter_obj(dict)
        """
        filter_obj = self.filter_collection.find_one({'_id': filter_id})

        return filter_obj

    def stash_filter(self, filter_obj, institute_id, user_id):

        filter_interface_version = __version__

        LOG.info("Stashing filter for user '%s' and institute %s, version %s",
            user_id, institute_id, filter_interface_version)
        result = self.filter_collection.insert_one(filter_obj)

        filter_id = result.inserted_id

        # log event
        self.create_event(institute=institute_obj, case=case_obj, user=user_obj,
            link=filter_id, category='case', verb='filter_stash', subject=individual['display_name'],
            level='global')

        return filter_id

    def filters(self, institute_id, variant_type):

        filters_res = self.filter_collection.find(
            {'institute_id': institute_id, 'variant_type': variant_type})

        return filters_res
