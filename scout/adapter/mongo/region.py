import logging
from typing import Optional

from scout.models.region import IscaRegion, Region

LOG = logging.getLogger(__name__)


def get_overlap_coords_query(start: int, end: int) -> list:
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

    def get_regions(self, build: str = "37", query: str = None) -> list:
        """Get all regions for a build."""
        filter_query = {"build": build}

        if query:
            filter_query.update(query)

        return list(self.region_collection.find(filter_query))

    def get_isca_regions(self, build: str = "37", query: str = None) -> list[IscaRegion]:
        """Get all ISCA regions for a build."""
        filter_query = {"isca_id": {"$exists": True}, "build": build}

        if query:
            filter_query.update(query)

        return list(self.region_collection.find(filter_query))

    def region_type_count(self) -> list:
        """Return the count of regions for each type in the db"""
        query = {"$group": {"_id": {"source": "$source", "build": "$build"}, "count": {"$sum": 1}}}
        return list(self.region_collection.aggregate([query]))

    def load_region(self, region_data: dict):
        """Load a region into the collection."""

        return self.region_collection.insert_one(region_data)

    def load_regions(self, regions_data: list):
        """Load multiple ISCA regions into the collection."""
        isca_regions = []
        for parsed_region in regions_data:
            coords = split_coords_according_to_build(parsed_region)
            for build in ["37", "38"]:
                if coords[build]:
                    parsed_region["chromosome"] = coords[build]["chrom"].lstrip("chr")
                    parsed_region["start"] = int(coords[build]["start"])
                    parsed_region["end"] = int(coords[build]["end"])
                    parsed_region["build"] = build

                    isca_region = IscaRegion(**parsed_region).model_dump(exclude_none=True)
                    isca_regions.append(isca_region)

        LOG.info("Inserting %d ISCA regions", len(isca_regions))
        self.region_collection.insert_many(isca_regions)

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
            "$or": get_overlap_coords_query(start, end),
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


def split_coords_according_to_build(parsed_region: dict) -> dict:
    """Split the coordinates of a parsed region according to the build.

    Each build coord is in the format "chrom:start-end". This function splits the coordinates into a dictionary with keys "37" and "38" for each build.
    """

    coords = {"37": {}, "38": {}}
    if parsed_region.get("build_37_coordinates"):
        coords["37"]["chrom"] = parsed_region.get("build_37_coordinates").split(":")[0]
        coords["37"]["start"] = (
            parsed_region.get("build_37_coordinates").split(":")[1].split("-")[0]
        )
        coords["37"]["end"] = parsed_region.get("build_37_coordinates").split(":")[1].split("-")[1]

    if parsed_region.get("build_38_coordinates"):
        coords["38"]["chrom"] = parsed_region.get("build_38_coordinates").split(":")[0]
        coords["38"]["start"] = (
            parsed_region.get("build_38_coordinates").split(":")[1].split("-")[0]
        )
        coords["38"]["end"] = parsed_region.get("build_38_coordinates").split(":")[1].split("-")[1]

    return coords
