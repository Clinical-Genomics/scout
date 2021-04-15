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
        LOG.debug(f"Inserting {len(cytobands)} cytoband intervals into database")
        result = self.cytoband_collection.insert_many(cytobands)
        LOG.debug(f"Number of inserted documents:{len(result.inserted_ids)}")

    def cytoband_by_chrom(self, build="37"):
        """Returns a dictionary of cytobands with chromosomes as keys

        Args:
            build(str): "37" or "38"

        Returns:
            cytobands_by_chrom_obj(dict). Something like this:
                {
                    "1": [
                        {
                            "band": "p36.33",
                            "chrom": "1",
                            "start": 0,
                            "stop": "2300000",
                        },
                        list of cytobands for chr1
                        ..
                    ],
                    "2" : [
                        list of cytobands for chr2
                    ]
                }

        """
        if "38" in str(build):
            build = "38"
        else:
            build = "37"

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
        cytobands_by_chrom = {each.pop("_id"): each for each in result}
        return cytobands_by_chrom
