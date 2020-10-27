# -*- coding: utf-8 -*-
import logging
from bson.objectid import ObjectId
from flask import url_for

import pymongo

LOG = logging.getLogger(__name__)


class FilterHandler(object):
    """Class to handle persistent variant filters in the mongo adapter"""

    def retrieve_filter(self, filter_id):
        """Retrieve a known stored filter object from the db

        Arguments:
            filter_id(str) - a unique id cast to ObjectId

        Returns:
            filter_obj(dict)
        """
        filter_obj = None
        LOG.debug("Retrieve filter {}".format(filter_id))
        filter_obj = self.filter_collection.find_one({"_id": ObjectId(filter_id)})
        if filter_obj is not None:
            # use _id to preselect the currently loaded filter, and drop it while we are at it
            filter_obj.update([("filters", filter_obj.pop("_id", None))])
        return filter_obj

    def stash_filter(
        self, filter_obj, institute_obj, case_obj, user_obj, category="snv", link=None
    ):
        """Store away filter settings for later use.

        Arguments:
            filter_obj(MultiDict)
            institute_obj(dict)
            user_obj(dict)
            case_obj(dict)
            category(str): in ['cancer', 'snv', 'str', 'sv']

        Returns:
            filter_id(str) - a unique id that can be cast to ObjectId
        """

        LOG.info(
            "Stashing filter for user '%s' and institute %s.",
            user_obj.get("email"),
            institute_obj.get("display_name"),
        )

        LOG.info("Filter object {}".format(filter_obj))

        institute_id = institute_obj.get("_id")
        filter_dict = {"institute_id": institute_id, "category": category}

        # make up a default display name
        filter_dict["display_name"] = (
            institute_obj.get("display_name") + "-" + case_obj.get("display_name")
        )

        for (element, value) in filter_obj.lists():
            if value == [""]:
                continue
            if element in ["save_filter", "filters", "csrf_token"]:
                continue
            if element == "filter_display_name":
                # filter display_name if given
                # will appear as the only element in an array
                filter_dict["display_name"] = value[0]
                continue
            filter_dict[element] = value

        result = self.filter_collection.insert_one(filter_dict)

        filter_id = result.inserted_id

        # log event
        subject = institute_obj["display_name"]

        # link e.g. to the variants view where filter was created
        if link is None:
            variants_target_from_category = {
                "sv": "variants.sv_variants",
                "cancer": "variants.cancer_variants",
                "snv": "variants.variants",
                "str": "variants.str_variants",
            }
            target = variants_target_from_category.get(category)

            case_name = case_obj.get("display_name")
            # filter dict already contains institute_id=institute_id,
            link = url_for(target, case_name=case_name, **filter_dict)

        self.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=link,
            category="case",
            verb="filter_stash",
            subject=subject,
            level="global",
        )

        return filter_id

    def delete_filter(self, filter_id, institute_id, user_id):
        """Delete a filter.

        Arguments:
            filter_id(str)
            institute_id(str)
            user_id(str)

        Returns:
            result()
        """
        filter_obj = self.filter_collection.find_one({"_id": ObjectId(filter_id)})
        if filter_obj is None:
            return

        LOG.info(
            "User {} deleting filter {} for institute {}.".format(
                user_id, filter_obj.get("display_name"), institute_id
            )
        )

        result = self.filter_collection.delete_one({"_id": ObjectId(filter_id)})

        return result

    def filters(self, institute_id, category="snv"):
        """Obtain a cursor for all filters available to an institute in a category.

        Arguments:
            institute_id(str)
            category(str): in ['cancer', 'snv', 'str', 'sv']

        Returns:
            filters(pymongo.Cursor)
        """
        filters_res = self.filter_collection.find(
            {"institute_id": institute_id, "category": category}
        )

        return filters_res
