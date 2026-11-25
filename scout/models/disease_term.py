from typing import List, Optional

from pydantic import BaseModel, field_validator


class ClinGenGeneValidity(BaseModel):
    """A ClinGen gene-disease validity curation for one gene of a MONDO disease term."""

    hgnc_id: int
    hgnc_symbol: str
    inheritance: Optional[str] = None  # ClinGen mode of inheritance, e.g. AD, AR, XL, SD, MT, UD
    classification: str  # example: Definitive
    online_report: Optional[str] = None
    date: Optional[str] = None
    gcep: Optional[str] = None  # Gene Curation Expert Panel


class DiseaseTerm(BaseModel):
    """Values that populate this class are parsed from files downloaded from OMIM
    (https://www.omim.org/), Orphadata (https://www.orphadata.com/) and
    ClinGen gene-disease validity curations (https://search.clinicalgenome.org/kb/gene-validity).
    """

    # _id: str # same as disease_id,  will be present in the disease term saved in the database
    disease_id: str  # example: OMIM:600233
    disease_nr: int  # example: 600233
    description: str
    source: str
    genes: Optional[List[int]] = []  # List of HGNC IDs
    inheritance: Optional[list] = []
    hpo_terms: Optional[List[str]] = []  # List of HPO terms associated with the disease
    clingen_gene_validity: Optional[List[ClinGenGeneValidity]] = []  # MONDO terms from ClinGen

    @field_validator("disease_nr", mode="before")
    def set_disease_nr(cls, disease_nr: str) -> Optional[int]:
        if disease_nr:
            return int(disease_nr)
