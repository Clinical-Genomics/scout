# -*- coding: utf-8 -*-
import logging

LOG = logging.getLogger(__name__)


class CytobandHandler(object):
    """Class to handle cytoband-related entries"""

    def add_cytobands(self, cytobands):
        """Adds a list of cytoband objects to database

        Args:
            cytobands(list): a list of cytobands objects

        """
        result = self.cytoband_collection.insert_many(cytobands)
        LOG.info(f"Number of inserted documents:{len(result.inserted_ids)}")
