import logging
from datetime import datetime
from fractions import Fraction
from pathlib import Path

import path

LOG = logging.getLogger(__name__)

from enum import Enum
from typing import Optional, Union, List, Dict, Literal

from pydantic import BaseModel, field_validator, model_validator, Field
from scout.constants import ANALYSIS_TYPES

SAMPLES_FILE_PATH_CHECKS = ["bam_file", "mitodel_file", "rhocall_bed", "rhocall_wig", "rna_coverage_bigwig",
                            "splice_junctions_bed", "tiddit_coverage_wig", "upd_regions_bed", "upd_sites_bed",
                            "vcf2cytosure"]

GENOME_BUILDS = ["37", "38"]


class PhenoType(str, Enum):
    affected = "affected"
    unaffected = "unaffected"


class Sex(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


def _get_demo_file_absolute_path(partial_path: str) -> str:
    """returns the absolute path to a given demo file."""
    APP_ROOT: str = path.abspath(path.join(path.dirname(__file__), ".."))
    return path.join(APP_ROOT, partial_path)


def _is_string_path(string_path) -> bool:
    return Path(string_path).is_file() or Path(_get_demo_file_absolute_path(partial_path=string_path))


#### Samples - related pydantic models ####

class BioNanoAccess(BaseModel):
    project: Optional[str] = None
    sample: Optional[str] = None


class ChromographImages(BaseModel):
    autozygous: Optional[str] = None
    coverage: Optional[str] = None
    upd_regions: Optional[str] = None
    upd_sites: Optional[str] = None


class Mitodel(BaseModel):
    discordant: Optional[int] = None
    normal: Optional[int] = None
    ratioppk: Optional[float] = None


class REViewer(BaseModel):
    alignment: Optional[str] = None
    alignment_index: Optional[str] = None
    vcf: Optional[str] = None
    catalog: Optional[str] = None
    reference: Optional[str] = None
    reference_index: Optional[str] = None


class SampleLoader(BaseModel):
    alignment_path: Optional[str] = None
    analysis_type: Literal[ANALYSIS_TYPES] = None
    bam_file: Optional[str] = ""
    bam_path: Optional[str] = None
    bionano_access: Optional[BioNanoAccess] = None
    capture_kits: Optional[str] = Field(alias="capture_kit")
    chromograph_images: Optional[ChromographImages] = ChromographImages()
    confirmed_parent: Optional[bool] = None
    confirmed_sex: Optional[bool] = None
    display_name: Optional[str] = None
    father: Optional[str] = None
    individual_id: str = Field(alias="sample_id")
    is_sma: Optional[str] = None
    is_sma_carrier: Optional[str] = None
    mitodel_file: Optional[str] = None
    mitodel: Optional[Mitodel] = Mitodel()
    mother: Optional[str] = None
    msi: Optional[str] = None
    mt_bam: Optional[str] = None
    phenotype: Literal["affected", "unaffected", "unknown"]
    predicted_ancestry: Optional[str] = None
    reviewer: Optional[REViewer] = REViewer()
    rhocall_bed: Optional[str] = None
    rhocall_wig: Optional[str] = None
    rna_coverage_bigwig: Optional[str] = None
    sample_name: Optional[str] = None
    sex: Literal["unknown", "female", "male"]
    smn1_cn: Optional[int] = None
    smn2_cn: Optional[int] = None
    smn2delta78_cn: Optional[int] = None
    smn_27134_cn: Optional[int] = None
    splice_junctions_bed: Optional[str] = None
    tiddit_coverage_wig: Optional[str] = None
    tissue_type: Optional[str] = None
    tmb: Optional[str] = None
    tumor_purity: Optional[float] = 0.0
    tumor_type: Optional[str] = None
    upd_regions_bed: Optional[str] = None
    upd_sites_bed: Optional[str] = None
    vcf2cytosure: Optional[str] = None

    @model_validator(mode='before')
    def set_sample_display_name(cls, values) -> 'SampleLoader':
        values.update(
            {"display_name": values.get("display_name", values.get("sample_name", values.get("individual_id")))})
        return values

    @model_validator(mode='before')
    def set_alignment_path(cls, values) -> 'SampleLoader':
        values.update({"bam_file": values.get("alignment_path", values.get("bam_file", values.get("bam_path")))})
        return values

    @model_validator(mode='before')
    def validate_file_path(cls, values) -> 'SampleLoader':
        for item in SAMPLES_FILE_PATH_CHECKS:
            if values.get(item) is None:
                continue
            if _is_string_path(values[item]) is True:
                return values
            else:
                raise ValueError(f"{item} path '{values[item]}' is not valid.")

    @field_validator("tumor_purity", mode="before")
    @classmethod
    def set_tumor_purity(cls, value: Union[str, float]) -> float:
        if isinstance(value, str):
            return float(Fraction(value))
        return value

    @field_validator("capture_kits", mode="before")
    @classmethod
    def set_capture_kits(cls, value: Union[str, List[str]]) -> List:
        if isinstance(value, str):
            return [value]
        return value


#### Case - related pydantic models ####

class CaseLoader(BaseModel):
    owner: str
    family: str
    family_name: str
    lims_id: Optional[str]
    synopsis: Optional[Union[List, str]]
    phenotype_terms: Optional[List] = []
    samples: List[SampleLoader]
    custom_images: Dict[str, str]
    vcf_snv: Optional[str]
    vcf_sv: Optional[str]
    vcf_str: Optional[str]
    vcf_mei: Optional[str]
    vcf_snv_research: Optional[str]
    vcf_sv_research: Optional[str]
    vcf_mei_research: Optional[str]
    smn_tsv: Optional[str]
    madeline: Optional[str]
    analysis_date: Optional[datetime] = datetime.now()
    human_genome_build: Union[str, int]
    delivery_report: Optional[str]
    gene_fusion_report: Optional[str]
    exe_ver: Optional[str]
    reference_info: Optional[str]
    rank_model_version: Optional[str]
    sv_rank_model_version: Optional[str]
    rank_score_threshold: Optional[int]
    default_gene_panels: List[str]
    gene_panels: List[str]
    peddy_ped: Optional[str]  # Soon to be deprecated
    peddy_check: Optional[str]  # Soon to be deprecated
    peddy_sex: Optional[str]  # Soon to be deprecated

    @field_validator("human_genome_build", mode="before")
    @classmethod
    def format_build(cls, value: Union[str, int]) -> str:
        str_build: str = str(value)
        if str_build in GENOME_BUILDS:
            return str_build
        else:
            raise ValueError("Genome build must be either '37' or '38'.")
