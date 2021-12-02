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

    def load_indexes(self, collections=[]):
        """Add the proper indexes to the scout instance.
        Args:
            collections(list): list of collections to update indexes for.
                               If empty, load indexes for all collections.
        """
        LOG.info(f"Adding indexes for collections: {collections or list(INDEXES.keys())}")
        for collection_name in collections or INDEXES:
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

    def update_indexes(self, collections=[]):
        """Update the indexes

        Args:
            collections(list): list of collections to update indexes for.
                               If empty, update indexes for all collections.
        """
        LOG.info(f"Updating indexes for collections: {collections or list(INDEXES.keys())}")
        nr_updated = 0

        for collection_name in collections or INDEXES:
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
