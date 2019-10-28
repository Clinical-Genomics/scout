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
                filter_display_id(str)

            Returns:
                filter_obj(dict)
        """
        LOG.debug("Retrieve filter {}".format(filter_id))
        filter_obj = self.filter_collection.find_one({'_id': ObjectId(filter_id)})

        # use _id to preselect the currently loaded filter, and drop it while we are at it
        filter_obj.update([('filters', filter_obj.pop('_id', None))])
        return filter_obj

    def stash_filter(self, filter_obj, institute_obj, case_obj, user_obj, category='snv'):
        """Store away filter settings for later use.

            Arguments:
                filter_obj(MultiDict)
                institute_obj(str)
                user_obj(str)
                category(str): in ['cancer', 'snv', 'str', 'sv'].

            Returns:
                filter_id(str)
        """
        filter_interface_version = __version__

        LOG.info("Stashing filter for user '%s' and institute %s, version %s",
            user_obj.get('email'), institute_obj.get('display_name'), filter_interface_version)

        LOG.info("Filter object {}".format(filter_obj))

        institute_id = institute_obj.get('_id')
        filter_dict = {'institute_id': institute_id,
            'category': category,}

        # make up a default display name
        filter_dict['display_name'] = institute_obj.get(
                'display_name') + "-" + case_obj.get('display_name')

        for (element, value) in filter_obj.lists():
            if value == ['']:
                continue
            if element == 'save_filter':
                continue
            if element == 'filter_display_name':
                # filter display_name if given
                filter_dict['display_name'] = value[0]
                continue
            filter_dict[element] = value

        result = self.filter_collection.insert_one(filter_dict)

        filter_id = result.inserted_id

        # log event
        subject = institute_obj['display_name']
        # clever link - eg url_for load filter?
        link = "filter/" + str(filter_id)
        # snv, sv, str..

        self.create_event(institute=institute_obj, case=case_obj, user=user_obj,
            link=link, category='case', verb='filter_stash', subject=subject,
            level='global')

        return filter_id

    def delete_filter(self, filter_id, institute_id, user_id):

        return

    def filters(self, institute_id, category="snv"):

        filters_res = self.filter_collection.find(
            {'institute_id': institute_id, 'category': category})

        return filters_res
