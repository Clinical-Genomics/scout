from typing import Optional

from pydantic import BaseModel


class Region(BaseModel):
    """A region in the genome"""

    build: str = "37"
    chromosome: str
    start: int
    end: int

    source: Optional[str] = None
    display_name: Optional[str] = None


class IscaRegion(Region):
    """A region in the genome with an ISCA id. ClinGen manage ISCA ids for ISCA, and provide
    haploinsufficiency and triplosensitivity information for the region."""

    isca_id: str

    source: str = "ClinGen ISCA"
    haploinsufficiency: Optional[str] = None
    triplosensitivity: Optional[str] = None
