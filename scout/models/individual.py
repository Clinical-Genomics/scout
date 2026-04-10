"""Pydantic models for Individual entity used in database operations."""

import logging
import os
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from scout.constants import ANALYSIS_TYPES, REV_PHENOTYPE_MAP
from scout.exceptions import PedigreeError

LOG = logging.getLogger(__name__)

# File paths that can be validated for existence
INDIVIDUAL_FILE_PATHS = [
    "assembly_alignment_path",
    "bam_file",
    "d4_file",
    "minor_allele_frequency_wig",
    "mt_bam",
    "paraphase_alignment_path",
    "phase_blocks",
    "rhocall_bed",
    "rhocall_wig",
    "rna_alignment_path",
    "rna_coverage_bigwig",
    "splice_junctions_bed",
    "tiddit_coverage_wig",
    "upd_regions_bed",
    "upd_sites_bed",
    "vcf2cytosure",
]


class FshdLocus(BaseModel):
    """BioNano FSHD D4Z4 locus data."""

    mapid: str
    chromosome: str
    haplotype: str
    count: str
    spanning_coverage: str


class Individual(BaseModel):
    """Pydantic model representing an Individual entity in the database.

    This model ensures all required fields are populated and validates data types
    before database insertion. It provides a stricter interface than the dict-based
    approach while maintaining all original functionality.
    """

    # Required fields
    individual_id: str
    display_name: str
    sex: str = "0"  # Default to unknown (0)
    phenotype: int = 0  # Default to unknown (0)

    # Family relationships
    father: Optional[str] = None
    mother: Optional[str] = None

    # Sample information
    capture_kits: List[str] = Field(default_factory=list)
    subject_id: Optional[str] = None

    # Alignment and data files
    bam_file: Optional[str] = None
    assembly_alignment_path: Optional[str] = None
    d4_file: Optional[str] = None
    mt_bam: Optional[str] = None
    rna_alignment_path: Optional[str] = None
    paraphase_alignment_path: Optional[str] = None
    phase_blocks: Optional[str] = None

    # Coverage and variant files
    minor_allele_frequency_wig: Optional[str] = None
    rhocall_bed: Optional[str] = None
    rhocall_wig: Optional[str] = None
    rna_coverage_bigwig: Optional[str] = None
    splice_junctions_bed: Optional[str] = None
    tiddit_coverage_wig: Optional[str] = None
    upd_regions_bed: Optional[str] = None
    upd_sites_bed: Optional[str] = None
    vcf2cytosure: Optional[str] = None

    # Quality control
    confirmed_sex: Optional[bool] = None
    confirmed_parent: Optional[bool] = None
    predicted_ancestry: Optional[str] = None

    # Analysis type
    analysis_type: str = "unknown"

    # Cancer-specific fields
    hrd: Optional[str] = None
    msi: Optional[str] = None
    tmb: Optional[str] = None
    tumor_purity: Optional[Union[str, float]] = None
    tumor_type: Optional[str] = None
    tissue_type: str = "unknown"

    # Chromograph images
    chromograph_images: Optional[Union[str, dict]] = None
    reviewer: Optional[Union[str, dict]] = None

    # SMA-specific fields
    is_sma: Optional[bool] = None
    is_sma_carrier: Optional[bool] = None
    smn1_cn: Optional[int] = None
    smn2_cn: Optional[int] = None
    smn2delta78_cn: Optional[int] = None
    smn_27134_cn: Optional[int] = None

    # Mitochondrial deletion analysis
    mitodel: Optional[dict] = None
    mitodel_file: Optional[str] = None

    # Paraphrase
    paraphrase: Optional[dict] = None

    # BioNano FSHD
    bionano_access: Optional[dict] = None
    fshd_loci: Optional[List[FshdLocus]] = None

    # Omics
    omics_sample_id: Optional[str] = None

    @model_validator(mode="before")
    def validate_required_fields(cls, values):
        """Validate required fields are present."""
        if "individual_id" not in values or not values["individual_id"]:
            raise PedigreeError("Individual is missing individual_id")
        return values

    @field_validator("sex", mode="before")
    @classmethod
    def convert_sex(cls, sex):
        """Convert sex to string representation (1/2/0)."""
        if sex is None or sex == "unknown" or sex == "0":
            return "0"

        # Try to parse as integer (already in ped format)
        if isinstance(sex, (int, str)):
            try:
                sex_int = int(sex)
                if sex_int not in [0, 1, 2]:
                    raise PedigreeError(f"Unknown sex: {sex}")
                return str(sex_int)
            except (ValueError, TypeError):
                pass

        # Try to map from string representation
        sex_lower = str(sex).lower()
        if sex_lower == "male":
            return "1"
        elif sex_lower == "female":
            return "2"
        elif sex_lower == "unknown":
            return "0"
        else:
            raise PedigreeError(f"Unknown sex: {sex}")

    @field_validator("phenotype", mode="before")
    @classmethod
    def convert_phenotype(cls, phenotype):
        """Convert phenotype to int representation (1/2/0)."""
        if phenotype is None or phenotype == "unknown":
            return 0

        # Try string mapping first
        try:
            ped_phenotype = REV_PHENOTYPE_MAP.get(phenotype)
            if ped_phenotype == -9:
                return 0
            if ped_phenotype in [0, 1, 2]:
                return ped_phenotype
        except (KeyError, AttributeError):
            pass

        # Try to parse as integer
        try:
            phen_int = int(phenotype)
            if phen_int in [0, 1, 2, -9]:
                return 0 if phen_int == -9 else phen_int
            raise PedigreeError(f"Unknown phenotype: {phenotype}")
        except (ValueError, TypeError):
            raise PedigreeError(f"Unknown phenotype: {phenotype}")

    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(cls, analysis_type):
        """Validate analysis type is in allowed list."""
        if analysis_type not in ANALYSIS_TYPES:
            raise PedigreeError(f"Analysis type '{analysis_type}' not allowed")
        return analysis_type

    @model_validator(mode="before")
    def process_file_paths(cls, values):
        """Convert relative paths to absolute paths if they exist."""
        for file_key in INDIVIDUAL_FILE_PATHS:
            file_path = values.get(file_key)
            if file_path and os.path.exists(file_path):
                values[file_key] = os.path.abspath(file_path)
            elif file_path:
                # Keep the path but log that it doesn't exist
                values[file_key] = None
        return values

    @model_validator(mode="before")
    def set_display_name(cls, values):
        """Ensure display_name is set."""
        if not values.get("display_name"):
            values["display_name"] = values.get("individual_id", "unknown")
        return values

    def to_dict(self) -> dict:
        """Convert model to dictionary for database insertion."""
        return self.model_dump(exclude_none=False)
