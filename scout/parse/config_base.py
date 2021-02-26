"""Class to hold information about scout load config"""

import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, validator, Field, root_validator
from typing_extensions import Literal
from fractions import Fraction
from scout.exceptions import ConfigError, PedigreeError
from pathlib import Path
from scout.utils.date import get_date


import logging

LOG = logging.getLogger(__name__)


class ChromographImages(BaseModel):
    autozygous: Optional[str] = None
    coverage: Optional[str] = None
    upd_regions: Optional[str] = None
    upd_sites: Optional[str] = None


# TODO: handle bam_path_options
class ScoutIndividual(BaseModel):
    alignment_path: Optional[str] = None
    analysis_type: Literal["wgs", "wes", "mixed", "unknown", "panel", "external"] = None
    bam_file: Optional[str] = ""
    bam_path: Optional[str] = None
    capture_kits: Optional[str] =  Field([], alias="capture_kit")
    chromograph_images: ChromographImages = ChromographImages()
    confirmed_parent: Optional[bool] = None
    confirmed_sex: Optional[bool] = None
    display_name: Optional[str] = None
    father: Optional[str] = None
    individual_id: str = Field(..., alias="sample_id")
    is_sma: Optional[str] = None
    is_sma_carrier: Optional[str] = None
    mother: Optional[str] = None
    msi: Optional[str] = None
    mt_bam: Optional[str] = None
    phenotype: Literal["affected", "unaffected", "unknown"] = None
    predicted_ancestry: str = None  ## ??
    rhocall_bed: Optional[str] = None
    rhocall_wig: Optional[str] = None
    sample_id: str = None
    sample_name: Optional[str] = None
    sex: Literal["male", "female", "unknown"] = None
    smn1_cn: int = None
    smn2_cn: int = None
    smn2delta78_cn: int = None
    smn_27134_cn: int = None
    tiddit_coverage_wig: Optional[str] = None
    tissue_type: Optional[str] = None
    tmb: Optional[str] = None
    tumor_purity: float = 0.0
    tumor_type: Optional[str] = None
    upd_regions_bed: Optional[str] = None
    upd_sites_bed: Optional[str] = None
    vcf2cytosure: Optional[str] = None

    @validator("sample_id", "sex", "phenotype")
    def mandatory_sample_id(cls, value):
        if value is None:
            raise PedigreeError("Sample, config error: '{}'".format(value))
        return value

    @validator("display_name")
    def fallback_display_name(cls, value):
        # TODO: set to 1. sample_name 2. sample_id
        LOG.debug("individual display_name: {}".format(value))
        return value

    @validator("tumor_purity")
    def cast_to_float(cls, value):
        if isinstance(value, str):
            return float(Fraction(value))
        return value

    @validator("capture_kits")
    def cast_to_string(cls, value):
        if isinstance(value, str):
            return [value]
        return value


    @root_validator
    def update_track(cls, values):
        # bam files have different aliases
        if values.get("alignment_path"):
            values.update({"bam_file": values.get("alignment_path")})
            return values
        elif values.get("bam_file"):
            # Dont't touch anything
            return values
        elif values.get("bam_path"):
            values.update({"bam_file": values.get("bam_path")})
            return values
        else:
            return values

    @root_validator
    def update_track_sample_id(cls, values):
        # set display_name to 1. sample_name
        #                     2. sample_id
        if values.get("sample_name"):
            values.update({"display_name": values.get("sample_name")})
            return values
        elif values.get("sample_id"):
            # Dont't touch anything
            values.update({"display_name": values.get("sample_id")})
            return values
        else:
            return values


# VCF Files
class VcfFiles(BaseModel):
    vcf_cancer: Optional[str] = None
    vcf_cancer_research: Optional[str] = None
    vcf_cancer_sv: Optional[str] = None
    vcf_cancer_sv_research: Optional[str] = None
    vcf_snv: Optional[str] = None
    vcf_snv_research: Optional[str] = None
    vcf_str: Optional[str] = None
    vcf_sv: Optional[str] = None
    vcf_sv_research: Optional[str] = None


# TODO: handle arguments used as alternative input
# TODO: validator to set track="cancer" if vcf_cancer||vcf_cancer_sv
# TODO: parse_ped seems to work on yet another file with pedigree info
# TODO: raise ConfigError
# TODO: synopsis kan vara både string och lista av strings som konkateneras med '.'
# TODO: collaborators ska vara lista
# TODO: vcf_files as class/dict
# XXX: why is madeline stored as a file_object?
class ScoutLoadConfig(BaseModel):
    analysis_date: Any = datetime.datetime.now()
    assignee: str = None  ## ??
    case_id: str = Field([], alias="family")  ## ??
    #  chromograph_image_files: Optional[List[str]]
    cnv_report: Optional[str] = None
    cohorts: Optional[List[str]] = None
    collaborators: Optional[List[str]] = None
    coverage_qc_report: str = None  ## ??
    default_panels: Optional[List[str]] = Field([], alias="default_gene_panels")
    delivery_report: Optional[str] = None
    display_name: str = Field([], alias="family_name")
    family: str = None
    gene_panels: Optional[List[str]] = []
    genome_build: str = Field([], alias="human_genome_build")
    human_genome_build: str = None
    individuals: List[ScoutIndividual] = Field([], alias="samples")  ## we also have samples ??
    lims_id: Optional[str] = None
    madeline_info: Optional[str] = Field("", alias="madeline")
    multiqc: Optional[str] = None
    owner: str = None
    peddy_check: Optional[str] = None
    peddy_ped: Optional[str] = None
    peddy_sex: Optional[str] = None
    phenotype_terms: Optional[List[str]] = None
    rank_model_version: Optional[str] = ""
    rank_score_threshold: int = 0
    samples: List[ScoutIndividual] = []
    smn_tsv: Optional[str] = None
    sv_rank_model_version: Optional[str] = ""
    synopsis: List[str] = None
    track: Literal["rare", "cancer"] = "rare"
    vcf_files: Optional[VcfFiles] = None

    @validator("analysis_date")
    def check_analysis_date(cls, dt):
        LOG.debug("GOT DATE: {}".format(dt))
        if isinstance(dt, datetime.datetime):
            LOG.debug("dt OK")
            # return datetime.datetime.strptime(dt, "%Y-%M-%d %H:%M%S")
            return dt
        correct_date = datetime.datetime.now()
        LOG.debug("returning {}".format(correct_date))
        return correct_date

    @validator("owner", pre=True, always=True)
    def mandatory_check_owner(cls, value):
        LOG.debug("OWNER: {}".format(value))
        if value is None:
            LOG.debug(" CHECK owner ConfigError owner")
            raise ConfigError("A case has to have a owner")
        return value

    @validator("family", pre=True, always=True)
    def mandatory_check_family(cls, value):
        LOG.debug("FAMILY: {}".format(value))
        if value is None:
            LOG.debug("RAISE ConfigError family")
            raise ConfigError("A case has to have a 'family'")
        return value

    @root_validator
    def update_track(cls, values):
        # Handle special circumstances
        vcfs = values.get("vcf_files")
        LOG.debug("VCFS: {}".format(vcfs))
        try:
            vcf_dict = vcfs.dict()
            if (
                vcf_dict["vcf_cancer"]
                or vcf_dict["vcf_cancer_research"]
                or vcf_dict["vcf_cancer_sv"]
                or vcf_dict["vcf_cancer_sv_research"]
            ):
                values.update({"track": "cancer"})
        except Exception as error:
            LOG.debug("exception in vcf_s?! {}".format(error))

        LOG.debug("OK")
        # Update collaborators to [owner] if not set
        if values.get("collaborators") is None:
            LOG.debug("UPDATE COLLAB")
            owner = values.get("owner")
            values.update({"collaborators": [owner]})
        LOG.debug("RETURN")
        return values

    @validator("madeline_info")
    def check_if_madelie_exists(cls, path):
        """Add the pedigree figure, this is a xml file which is dumped in the db"""
        mad_path = Path(path)
        if not mad_path.exists():
            raise ValueError("madeline path not found: {}".format(mad_path))
        with mad_path.open("r") as in_handle:
            return in_handle.read()

    @validator("track")
    def field_not_none(cls, v):
        if v is None:
            raise ValueError("Owner and family can not be None")
        return v

    @validator("synopsis")
    def synopsis_pre(cls, my_synopsis):
        if isinstance(my_synopsis, list):
            return ". ".join(my_synopsis)
        return my_synopsis

    class Config:
        validate_assignment = True
