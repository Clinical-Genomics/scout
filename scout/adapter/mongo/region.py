import logging

from models.region import IscaRegion

LOG = logging.getLogger(__name__)


class RegionHandler:
    """A class to handle regions in the genome."""

    def __init__(self, adapter):
        self.adapter = adapter

    def get_region(self, region_id: str, build: str = "37") -> Optional[Region]:
        """Get a region by its _id."""

        return self.region_collection.find_one({"_id": region_id, "build": build})

    def get_isca_region(self, isca_id: str, build: str = "37") -> Optional[IscaRegion]:
        """Get a region by its ISCA id."""

        return self.region_collection.find_one({"isca_id": isca_id, "build": build})

    def get_isca_regions(self, build: str = "37") -> list[IscaRegion]:
        """Get all ISCA regions for a build."""

        return list(self.region_collection.find({"isca_id": {"$exists": True}, "build": build}))

    def load_region(self, region_data: dict):
        """Load a region into the collection."""

        return self.region_collection.insert_one(region_data)

    def load_regions(self, regions_data: list):
        """Load multiple regions into the collection."""
        return self.region_collection.insert_many(regions_data)

    def drop_regions(self, build=None):
        """Delete the regions collection"""
        if build:
            LOG.info("Dropping the region collection, build %s", build)
            self.region_collection.delete_many({"build": str(build)})
        else:
            LOG.info("Dropping the region collection")
            self.region_collection.drop()

    def get_interval_overlapping_regions(
        self, chromosome: str, start: int, end: int, build: str = "37"
    ) -> list:
        """Get regions that overlap with a given region."""

        query = {
            "chromosome": chromosome,
            "build": build,
            "$or": self.get_overlap_coords_query(start, end),
        }

        return list(self.region_collection.find(query))

    def get_position_overlapping_regions(
        self, chromosome: str, position: int, build: str = "37"
    ) -> list:
        """Get regions that overlap with a given position."""

        query = {
            "chromosome": chromosome,
            "build": build,
            "start": {"$lte": position},
            "end": {"$gte": position},
        }

        return list(self.region_collection.find(query))

    def get_overlap_coords_query(self, start: int, end: int) -> list:
        """
        Here are the possible overlapping search scenarios:
         # Case 1
         # filter                 xxxxxxxxx
         # region           xxxxxxxx

         # Case 2
         # filter                 xxxxxxxxx
         # region                    xxxxxxxx

         # Case 3
         # filter                 xxxxxxxxx
         # region                   xx

         # Case 4
         # filter                 xxxxxxxxx
         # region             xxxxxxxxxxxxxx
        """
        return [
            # Overlapping cases 1-4 (chromosome == end_chrom)
            {"end": {"$gte": start, "$lte": end}},  # Case 1
            {"start": {"$gte": start, "$lte": end}},  # Case 2
            {
                "$and": [
                    {"start": {"$gte": start}},
                    {"end": {"$lte": end}},
                ]
            },  # Case 3
            {
                "$and": [
                    {"start": {"$lte": start}},
                    {"end": {"$gte": end}},
                ]
            },  # Case 4
        ]
