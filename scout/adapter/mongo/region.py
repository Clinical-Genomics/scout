from models.region import IscaRegion


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

    def drop_regions(self, build=None):
        """Delete the regions collection"""
        if build:
            LOG.info("Dropping the region collection, build %s", build)
            self.region_collection.delete_many({"build": str(build)})
        else:
            LOG.info("Dropping the region collection")
            self.region_collection.drop()
