from models.region import IscaRegion


class RegionHandler():
    """A class to handle regions in the genome."""

    def __init__(self, adapter):
        self.adapter = adapter


    def get_region(self, ):


    def get_isca_region(self, region_id: str, build: str = "37") -> Optional[IscaRegion]:
        """Get a region by its ISCA id."""

        return self.region_collection.find_one({"isca_id": region_id, "build": build})
