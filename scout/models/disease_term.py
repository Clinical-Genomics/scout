from typing import List, Optional

from pydantic import BaseModel


class DiseaseTerm(BaseModel):
    """Values that populate this class are parsed from files downloaded from OMIM:
    https://www.omim.org/
    """

    # _id
    disease_id: str  # example: OMIM:600233
    disease_nr: int  # example: 600233
    description: str
    source: str
    genes: Optional[List[int]] = []  # List of HGNC IDs
    inheritance: Optional[List[str]] = []
    hpo_terms: Optional[List[str]]  # List of HPO terms associated with the disease
