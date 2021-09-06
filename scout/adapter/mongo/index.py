# -*- coding: utf-8 -*-
import logging
import pymongo.errors as pymongo_errors

from scout.constants import INDEXES

LOG = logging.getLogger(__name__)


class IndexHandler(object):
    def indexes(self, collection=None):
        """Return a list with the current indexes

        Skip the mandatory _id_ indexes

        Args:
            collection(str)

        Returns:
            indexes(list)
        """

        indexes = []

        for collection_name in self.collections():
            if collection and collection != collection_name:
                continue
            for index_name in self.db[collection_name].index_information():
                if index_name != "_id_":
                    indexes.append(index_name)
        return indexes

    def load_indexes(self):
        """Add the proper indexes to the scout instance.

        All indexes are specified in scout/constants/indexes.py

        If this method is utilised when new indexes are defined those should be added

        """
        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get("name")
                if index_name in existing_indexes:
                    LOG.info("Deleting old index: %s" % index_name)
                    self.db[collection_name].drop_index(index_name)
            LOG.info(
                "creating indexes for {0} collection: {1}".format(
                    collection_name,
                    ", ".join([index.document.get("name") for index in indexes]),
                )
            )
            self.db[collection_name].create_indexes(indexes)

    def update_indexes(self):
        """Update the indexes

        If there are any indexes that are not added to the database, add those.

        """
        LOG.info("Updating indexes...")
        nr_updated = 0

        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get("name")
                if index_name not in existing_indexes:
                    nr_updated += 1
                    LOG.info("Adding index : %s" % index_name)
                    try:
                        self.db[collection_name].create_indexes([index])
                    except pymongo_errors.OperationFailure as op_failure:
                        LOG.warning(
                            "An Operation Failure occurred while updating Scout indexes: {}".format(
                                op_failure
                            )
                        )
                    except Exception as ex:
                        LOG.warning("An error occurred while updating Scout indexes: {}".format(ex))

        if nr_updated == 0:
            LOG.info("All indexes in place")

    def drop_indexes(self):
        """Delete all indexes for the database"""
        LOG.warning("Dropping all indexe")
        for collection_name in INDEXES:
            LOG.warning("Dropping all indexes for collection name %s", collection_name)
            self.db[collection_name].drop_indexes()
