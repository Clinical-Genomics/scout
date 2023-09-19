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

SAMPLES_FILE_PATH_CHECKS = [
    "bam_file",
    "mitodel_file",
    "rhocall_bed",
    "rhocall_wig",
    "rna_coverage_bigwig",
    "splice_junctions_bed",
    "tiddit_coverage_wig",
    "upd_regions_bed",
    "upd_sites_bed",
    "vcf2cytosure",
]

CASE_FILE_PATH_CHECKS = ["cnv_report", "coverage_qc_report", "delivery_report", "gene_fusion_report",
                         "gene_fusion_report_research", "madeline_info", "multiqc", "multiqc_rna", "peddy_ped",
                         "peddy_ped_check",
                         "peddy_sex_check", "RNAfusion_inspector", "RNAfusion_report", "RNAfusion_report_research",
                         "vcf_cancer", "vcf_cancer_research", "vcf_cancer_sv", "vcf_cancer_sv_research", "vcf_snv",
                         "vcf_snv_research", "vcf_mei", "vcf_mei_research", "vcf_str", "vcf_sv", "vcf_sv_research"]

GENOME_BUILDS = ["37", "38"]
TRACKS = ["rare", "cancer"]


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
    return Path(string_path).is_file() or Path(
        _get_demo_file_absolute_path(partial_path=string_path)
    )


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
    capture_kits: Optional[Union[str, List]] = Field(alias="capture_kit")
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

    @field_validator("tumor_purity", mode="before")
    @classmethod
    def set_tumor_purity(cls, value: Union[str, float]) -> float:
        if isinstance(value, str):
            return float(Fraction(value))
        return value

    @model_validator(mode="before")
    def set_sample_display_name(cls, values) -> "SampleLoader":
        values.update(
            {
                "display_name": values.get(
                    "display_name", values.get("sample_name", values.get("individual_id"))
                )
            }
        )
        return values

    @model_validator(mode="before")
    def set_alignment_path(cls, values) -> "SampleLoader":
        values.update(
            {
                "bam_file": values.get(
                    "alignment_path", values.get("bam_file", values.get("bam_path"))
                )
            }
        )
        return values

    @model_validator(mode='before')
    def validate_file_path(cls, values: Dict) -> 'SampleLoader':
        for item in SAMPLES_FILE_PATH_CHECKS:
            item_path: str = values.get(item)
            if item_path and _is_string_path(values[item]) is False:
                raise ValueError(f"{item} path '{values[item]}' is not valid.")

        return values

    @field_validator("capture_kits", mode="before")
    @classmethod
    def set_capture_kits(cls, value: Union[str, List[str]]) -> List:
        if isinstance(value, str):
            return [value]
        return value


#### Custom images - related classes ####

class Image(BaseModel):
    data: Optional[str] = None
    description: Optional[str] = None
    height: Optional[int] = None
    format: Optional[str] = None
    path: str = None
    str_repid: Optional[str] = None
    title: str = None
    width: Optional[int] = None


class RawCustomImages(BaseModel):
    """This class makes a preliminary check that custom_images in the load config file has the expected structure."""
    custom_images: Dict[str, Union[List[Image], Dict[str, List[Image]]]] = None


class ParsedCustomImages(BaseModel):
    variant_custom_images: Optional[Dict] = Field(alias="str")
    case_custom_images: Optional[Dict] = Field(alias="case")


#### Case - related pydantic models ####

class CaseLoader(BaseModel):
    analysis_date: Optional[datetime] = datetime.now()
    assignee: Optional[str] = None
    case_id: str = Field(alias="family")
    cnv_report: Optional[str] = None
    cohorts: Optional[List[str]] = None
    collaborators: Optional[List[str]] = None
    coverage_qc_report: Optional[str] = None
    custom_images: Union[RawCustomImages, ParsedCustomImages] = None
    default_panels: Optional[List[str]] = Field([], alias="default_gene_panels")
    delivery_report: Optional[str] = None
    display_name: Optional[str] = Field(alias="family_name")
    exe_ver: Optional[str] = None
    family: str = None
    gene_fusion_report: Optional[str] = None
    gene_fusion_report_research: Optional[str] = None
    gene_panels: Optional[List[str]] = []
    genome_build: Union[str, int] = Field(38, alias="human_genome_build")
    individuals: List[SampleLoader] = Field([], alias="samples")
    lims_id: Optional[str] = None
    madeline_info: Optional[str] = Field(None, alias="madeline")
    multiqc: Optional[str] = None
    multiqc_rna: Optional[str] = None
    owner: str = None
    peddy_ped: Optional[str] = None  # Soon to be deprecated
    peddy_ped_check: Optional[str] = Field(None, alias="peddy_check")  # Soon to be deprecated
    peddy_sex_check: Optional[str] = Field(None, alias="peddy_sex")  # Soon to be deprecated
    phenotype_terms: Optional[List[str]] = None
    rank_model_version: Optional[str] = None
    rank_score_threshold: Optional[int] = 0
    reference_info: Optional[str] = None
    RNAfusion_inspector: Optional[str] = None
    RNAfusion_inspector_research: Optional[str] = None
    RNAfusion_report: Optional[str] = None
    RNAfusion_report_research: Optional[str] = None
    smn_tsv: Optional[str] = None
    sv_rank_model_version: Optional[str] = None
    synopsis: Union[List[str], str] = None
    track: Literal["rare", "cancer"] = "rare"

    vcf_cancer: Optional[str] = None
    vcf_cancer_research: Optional[str] = None
    vcf_cancer_sv: Optional[str] = None
    vcf_cancer_sv_research: Optional[str] = None
    vcf_snv: Optional[str] = None
    vcf_snv_research: Optional[str] = None
    vcf_mei: Optional[str] = None
    vcf_mei_research: Optional[str] = None
    vcf_str: Optional[str] = None
    vcf_sv: Optional[str] = None
    vcf_sv_research: Optional[str] = None

    @field_validator("genome_build", mode="before")
    @classmethod
    def format_build(cls, value: Union[str, int]) -> str:
        str_build: str = str(value)
        if str_build in GENOME_BUILDS:
            return str_build
        else:
            raise ValueError("Genome build must be either '37' or '38'.")

    @model_validator(mode='before')
    def validate_file_path(cls, values: Dict) -> 'SampleLoader':
        for item in CASE_FILE_PATH_CHECKS:
            item_path: str = values.get(item)
            if item_path and _is_string_path(values[item]) is False:
                raise ValueError(f"{item} path '{values[item]}' is not valid.")

        return values
