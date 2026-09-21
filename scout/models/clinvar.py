from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel

from scout.constants import CHROMOSOMES
from scout.constants.clinvar import (
    CITATION_DBS_API,
    GERMLINE_CLASSIF_TERMS,
    ONCOGENIC_CLASSIF_TERMS,
)

### Models used for submissions via API

CitationDB = Enum("CitationDB", {db.upper(): db for db in CITATION_DBS_API})
OncogenicityClassificationDescription = Enum(
    "OncogenicityClassificationDescription",
    {term.upper().replace(" ", "_"): term for term in ONCOGENIC_CLASSIF_TERMS},
)

GermlineClassificationDescription = Enum(
    "GermlineClassificationDescription",
    {term.upper().replace(" ", "_"): term for term in GERMLINE_CLASSIF_TERMS},
)


class Citation(BaseModel):
    db: CitationDB
    id: str


class Classification(BaseModel):
    dateLastEvaluated: str
    comment: Optional[str] = None
    citation: Optional[List[Citation]] = None


class OncogenicityClassification(Classification):
    oncogenicityClassificationDescription: OncogenicityClassificationDescription


class GermlineClassification(Classification):
    germlineClassificationDescription: GermlineClassificationDescription


class ObservedIn(BaseModel):
    alleleOrigin: str
    affectedStatus: str
    collectionMethod: str
    numberOfIndividuals: int


class OncoObservedIn(ObservedIn):
    presenceOfSomaticVariantInNormalTissue: str
    somaticVariantAlleleFraction: Optional[float] = None


class Gene(BaseModel):
    symbol: str


Chromosome = Enum(
    "Chromosome", {c: c for c in CHROMOSOMES}
)  # ClinVar API accepts only 'MT' chromosome


class Variant(BaseModel):
    """It's defined by either coordinates or HGVS."""

    alternateAllele: Optional[str] = None
    assembly: Optional[Literal["GRCh37", "GRCh38"]] = None
    chromosome: Optional[Chromosome] = None
    gene: Optional[List[Gene]] = None
    hgvs: Optional[str] = None
    start: Optional[int] = None
    stop: Optional[int] = None
    innerStart: Optional[int] = None
    innerStop: Optional[int] = None
    outerStart: Optional[int] = None
    outerStop: Optional[int] = None


class VariantSet(BaseModel):
    variant: List[Variant]


class Condition(BaseModel):
    db: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None


class ConditionSet(BaseModel):
    condition: List[Condition]


class SubmissionItem(BaseModel):
    # Field necessary for the API submissions:
    recordStatus: str
    submittedAssembly: Optional[Literal["GRCh37", "GRCh38"]] = None
    variantSet: VariantSet
    conditionSet: ConditionSet

    # Fields necessary to map the variant to a variant in Scout:
    institute_id: str
    case_id: str
    case_name: str
    variant_id: str


class OncogenicitySubmissionItem(SubmissionItem):
    # Field necessary for the API submissions:
    oncogenicityClassification: OncogenicityClassification
    observedIn: List[OncoObservedIn]


class GermlineSubmissionItem(SubmissionItem):
    observedIn: List[ObservedIn]
    germlineClassification: GermlineClassification
