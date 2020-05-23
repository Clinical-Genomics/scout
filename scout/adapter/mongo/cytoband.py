# -*- coding: utf-8 -*-
import logging
import pymongo

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

    def cytoband_by_chrom(self, build="37"):
        """Returns a dictionary of cytobands with chromosomes as keys

        Args:
            build(str): "37" or "38"

        Returns:
            cytobands_obj(dict)

        """
        match = {"$match": {"build": build}}
        group = {
            "$group": {
                "_id": "$chrom",
                "cytobands": {
                    "$push": {
                        "band": "$band",
                        "chrom": "$chrom",
                        "start": "$start",
                        "stop": "$stop",
                    }
                },
            }
        }
        sort = {"$sort": {"start": pymongo.ASCENDING}}

        result = self.cytoband_collection.aggregate([match, group, sort])
        cytobands_by_chrom_obj = {each.pop("_id"): each for each in result}
        return cytobands_by_chrom_obj
