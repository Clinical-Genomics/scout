from datetime import date, datetime
from enum import Enum
from typing import List, Literal, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel

from scout.constants import CHROMOSOMES
from scout.constants.clinvar import CITATION_DBS_API, ONCOGENIC_CLASSIF_TERMS

"""Model of the document that gets saved/updated in the clinvar_submission collection
 for each institute that has cases with ClinVar submission objects"""
clinvar_submission = {
    "_id": ObjectId,
    "status": str,  # open, closed
    "created_at": datetime,
    "institute_id": str,
    "variant_data": list,
    "case_data": list,
    "updated_at": datetime,
    "clinvar_subm_id": str,
}

"""Model of one document that gets saved in the `clinvar` collection. Relative to a Variant object"""
clinvar_variant = {
    "_id": str,  # caseID_variantID. Example: "internal_id_4c7d5c70d955875504db72ef8e1abe77"
    "csv_type": str,  # "variant"
    "case_id": str,
    "category": str,  # "snv" or "sv"
    "local_id": str,  # _id of a scout variant
    "linking_id": str,  # same as local_id
    "gene_symbol": str,  # example: "POT1"
    "ref_seq": str,  # example: "NM_001042594"
    "hgvs": str,  # example: "c.510G>T"
    "chromosome": str,
    "end_chromosome": str,  # for SVs only
    "condition_id_type": str,  # enum: "HPO", "OMIM"
    "condition_id_value": str,  # example: HP:0001298;HP:0001250
    "condition_comment": str,
    "explanation_for_multiple_conditions": str,
    "start": int,
    "stop": int,
    "ref": str,
    "alt": str,
    "variations_ids": str,  # example: "rs116916706"
    "clinsig": str,  # example: "Pathogenic"
    "clinsig_comment": str,
    "clinsig_cit": str,
    "inheritance_mode": str,
    "last_evaluated": date,
    "assertion_method": str,  # default: "ACMG Guidelines, 2015"
    "assertion_method_cit": str,  # default: "PMID:25741868"
    "var_type": str,  # (only for SVs) example: "deletion"
    "ref_copy": int,  # (only for SVs) Copy number in reference allele
    "ncopy": int,  # (only for SVs) Copy number in alternative allele
    "breakpoint1": int,  # (only for SVs)
    "breakpoint2": int,  # (only for SVs)
    "outer_start": int,  # (only for SVs)
    "inner_start": int,  # (only for SVs)
    "inner_stop": int,  # (only for SVs)
    "outer_stop": int,  # (only for SVs)
}

"""Model of one document that gets saved in the `clinvar` collection. Relative to a CaseData object"""
clinvar_casedata = {
    "_id": str,  # caseID_VariantID_individualID. Example: "internal_id_4c7d5c70d955875504db72ef8e1abe77_NA12882"
    "csv_type": str,  # "casedata"
    "case_id": str,
    "linking_id": str,  # _id of a variant
    "individual_id": str,  # example: "NA12882"
    "collection_method": str,  # default: "clinical testing"
    "allele_origin": str,  # example: "germline"
    "is_affected": str,  # example: "yes"
    "sex": str,
    "fam_history": str,  # example: "no"
    "is_proband": str,  # example: "yes"
    "is_secondary_finding": str,  # example: "no"
    "is_mosaic": str,  # example: "no"
    "zygosity": str,  # example: "compound heterozygote"
    "platform_type": str,  # default: "next-gen sequencing"
    "platform_name": str,  # default: "Whole exome sequencing, Illumina"
    "method_purpose": str,  # default: "discovery"
    "reported_at": date,
}

### Models used for oncogenocity submissions via API


CitationDB = Enum("CitationDB", {db.upper(): db for db in CITATION_DBS_API})
OncogenicityClassificationDescription = Enum(
    "OncogenicityClassificationDescription",
    {term.upper().replace(" ", "_"): term for term in ONCOGENIC_CLASSIF_TERMS},
)


class Citation(BaseModel):
    db: CitationDB
    id: str


class OncogenicityClassification(BaseModel):
    oncogenicityClassificationDescription: OncogenicityClassificationDescription
    dateLastEvaluated: str
    comment: Optional[str] = None
    citation: Optional[List[Citation]] = None


class ObservedIn(BaseModel):
    alleleOrigin: str
    affectedStatus: str
    collectionMethod: str
    numberOfIndividuals: int
    presenceOfSomaticVariantInNormalTissue: str
    somaticVariantAlleleFraction: Optional[float] = None


class Gene(BaseModel):
    symbol: str


Chromosome = Enum(
    "Chromosome", {c: c for c in CHROMOSOMES}
)  # ClinVar API accepts only 'MT' chromosome


class Variant(BaseModel):
    """It's defined by either coordinates or hgvs."""

    alternateAllele: Optional[str] = None
    assembly: Optional[Literal["GRCh37", "GRCh38"]] = None
    chromosome: Optional[Chromosome] = None
    gene: Optional[List[Gene]] = None
    hgvs: Optional[str] = None
    start: Optional[int] = None
    stop: Optional[int] = None


class VariantSet(BaseModel):
    variant: List[Variant]


class Condition(BaseModel):
    db: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None


class ConditionSet(BaseModel):
    condition: List[Condition]


class OncogenicitySubmissionItem(BaseModel):
    # Field necessary for the API submissions:
    recordStatus: str
    oncogenicityClassification: OncogenicityClassification
    observedIn: List[ObservedIn]
    variantSet: VariantSet
    conditionSet: ConditionSet

    # Fields necessary to map the variant to a variant in Scout:
    institute_id: str
    case_id: str
    case_name: str
    variant_id: str
