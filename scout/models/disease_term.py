from typing import List, Optional, Union

from pydantic import BaseModel, field_validator


class DiseaseTerm(BaseModel):
    """Values that populate this class are parsed from files downloaded from OMIM:
    https://www.omim.org/
    """

    disease_id: str  # example: OMIM:600233
    disease_nr: int  # example: 600233
    description: str
    source: str
    hgnc_ids: Optional[List[int]] = []  # List of HGNC IDs
    inheritance: Optional[list] = []
    hpo_terms: Optional[List[str]]  # List of HPO terms associated with the disease

    @field_validator("disease_nr", mode="before")
    def set_disease_nr(cls, disease_nr: str) -> Optional[int]:
        if disease_nr:
            return int(disease_nr)
