# -*- coding: utf-8 -*-
import logging

log = logging.getLogger(__name__)

from scout.constants import INDEXES

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

        for collection_name in self.db.collection_names():
            if collection and collection != collection_name:
                continue
            for index_name in self.db[collection_name].index_information():
                if index_name != '_id_':
                    indexes.append(index_name)
        return indexes

    def load_indexes(self):
        """Add a hpo object

        Arguments:
            hpo_obj(dict)

        """
        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get('name')
                if index_name in existing_indexes:
                    log.info("Deleting old index: %s" % index_name)
                    self.db[collection_name].drop_index(index_name)
            log.info("creating indexes: %s" % ', '.join([
                index.document.get('name') for index in indexes
            ]))
            self.db[collection_name].create_indexes(indexes)
        

