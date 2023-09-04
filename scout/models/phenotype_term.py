from pydantic import BaseModel, validator
from typing import List, Optional


# Hpo terms represents data from the hpo web
class HpoTerm(BaseModel):
    _id: str
    hpo_id: str
    hpo_number: Optional[int]
    description: str
    ancestors: List = []
    all_ancestors: List = []
    children: List = []
    genes: List = []

    @validator("hpo_number", always=True)
    def get_hpo_number(cls, value, values) -> int:
        return int(values["hpo_id"].split(":")[-1])


# Disease terms represent diseases collected from omim, orphanet and decipher.
# Collected from OMIM
class DiseaseTerm(dict):
    """Represents a disease term

    _id = str, # Same as disease_id
    disease_id = str, # required, like OMIM:600233
    disease_nr = int, # The disease nr
    description = str, # required
    source = str, # required
    genes = list, # List with integers that are hgnc_ids
    inheritance = list, # List of inheritance models connected to the disease
    hpo_terms = list, # List of hpo terms associated with the disease

    """

    def __init__(
        self,
        disease_id,
        disease_nr,
        description,
        source,
        genes=None,
        inheritance=None,
        hpo_terms=None,
    ):
        super(DiseaseTerm, self).__init__()
        self["disease_id"] = disease_id
        self["_id"] = disease_id
        self["disease_nr"] = int(disease_nr)
        self["description"] = description
        self["source"] = source
        self["genes"] = genes or []
        self["inheritance"] = inheritance or []
        self["hpo_terms"] = hpo_terms or []


# phenotype_term is a special object to hold information on case level
# This one might be deprecated when we skip mongoengine
phenotype_term = dict(
    phenotype_id=str,
    feature=str,
    disease_models=list,  # Can be omim_id hpo_id  # list of strings
)
