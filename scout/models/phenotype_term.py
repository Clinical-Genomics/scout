import logging
from typing import List, Optional

from pydantic import BaseModel, model_validator

LOG = logging.getLogger(__name__)


# Hpo terms represents data from the hpo web
class HpoTerm(BaseModel):
    """
    Values that populate this class gets parsed from items present in the hpo.obo file:
    https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo
    """

    hpo_id: str  # id field in the hpo.obo file
    hpo_number: Optional[
        int
    ] = None  # id field in the hpo.obo file, stripped of the 'HP:' part and the zeroes
    description: str  # name field in the hpo.obo file
    ancestors: List = []
    all_ancestors: List = []
    children: List = []
    genes: List = []  # List with integers that are hgnc_ids

    @model_validator(mode="after")
    def set_hpo_number(self) -> "HpoTerm":
        self.hpo_number = int(self.hpo_id.split(":")[1])
        return self
