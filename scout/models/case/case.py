"""Models for Case and related entities used in database operations."""

from __future__ import absolute_import

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from scout.constants import CASE_STATUSES, PHENOTYPE_GROUPS

logger = logging.getLogger(__name__)

# Legacy dict-based type definitions (kept for reference)

individual = dict(
    individual_id=str,  # required
    display_name=str,
    sex=str,
    phenotype=int,
    father=str,  # Individual id of father
    mother=str,  # Individual id of mother
    capture_kits=list,  # List of names of capture kits
    bam_file=str,  # Path to bam file
    minor_allele_frequency_wig=str,  # Path to wig file
    rhocall_bed=str,  # Path to bed file
    rhocall_wig=str,  # Path to wig file
    tiddit_coverage_wig=str,  # Path to wig file
    upd_regions_bed=str,  # Path to bed file
    upd_sites_bed=str,  # Path to bed file
    vcf2cytosure=str,  # Path to CGH file
    analysis_type=str,  # choices: ANALYSIS_TYPES
    confirmed_sex=bool,  # True or False. None if no check has been done
    confirmed_parent=bool,
    is_sma=bool,  # True / False if SMA status determined - None if not done.
    is_sma_carrier=bool,  # True / False if SMA carriership determined - None if not done.
    smn1_cn=int,  # CopyNumber
    smn2_cn=int,  # CopyNumber
    smn2delta78_cn=int,  # CopyNumber
    smn_27134_cn=int,  # CopyNumber
    rna_alignment_path=str,  # Path to bam file
    rna_coverage_bigwig=str,  # Coverage islands generated from bam or cram files (RNA-seq analysis)
    omics_sample_id=str,  # RNA sample id for connected wts outliers
    splice_junctions_bed=str,  # An indexed junctions .bed.gz file obtained from STAR v2 aligner *.SJ.out.tab file.
    predicted_ancestry=str,  # one of AFR AMR EAS EUR SAS UNKNOWN
    tumor_type=str,
    tmb=str,
    msi=str,
    hrd=str,
    tumor_purity=float,
    tissue_type=str,
    chromograph_images=str,  # path to image files
    fshd_loci=list(
        dict(mapid=str, chromosome=str, haplotype=str, count=str, spanning_coverage=str)
    ),  # list of D4Z4 bionano access loci
)

case = dict(
    analysis_date=datetime,
    assignees=list,  # list of str _id of a user (email)
    beacon=dict,  # beacon submission dictionary {created_at: datetime, user: str(email), samples: list(dict), panels: list(dict), vcf_files: list(str)}
    case_id=str,  # required: True, unique. This is a string with the id for the family
    causatives=list,  # List of variants referred by there _id
    cnv_report=str,  # CNV report is a path to pdf file
    collaborators=list,  # List of institute_ids that are allowed to view the case
    coverage_qc_report=str,  # Covearge and qc report is a path to a html file
    created_at=datetime,
    delivery_report=str,  # delivery report is a path to html file
    diagnosis_genes=list,  # List of references to genes
    diagnosis_phenotypes=list,  # List of dictionaries with OMIM disease data
    display_name=str,  # required. This is the case name that will be shown in scout.
    dynamic_gene_list=list,  # List of genes
    gene_fusion_report=str,  # Path to the gene fusions report file
    gene_fusion_report_research=str,  # Path to the gene fusions research report file
    genome_build=str,  # This should be 37 or 38
    group=list,  # a list of group ids for cases conceptually grouped together with this
    has_meivariants=bool,  # default: False
    has_strvariants=bool,  # default: False
    has_svvariants=bool,  # default: False
    individuals=list,  # list of dictionaries with individuals
    is_migrated=bool,  # default: False
    is_research=bool,  # default: False
    madeline_info=str,  # madeline info is a full xml file
    mme_subission=dict,  # MME submission dictionary {created_at: datetime, updated_at: datetime, patients: list(), submission_user: str(user_id), sex: bool, features: list(dict(id:str, label:str, observed:str)), disorders: list(), genes_only: bool},
    multiqc=str,  # path to multiqc report
    multiqc_rna=str,  # path to multiqc RNA report
    owner=str,  # required. Internal_id for the owner of the case. E.g. 'cust000'
    panels=list,  # list of dictionaries with panel information.
    phenotype_groups=list,  # List of dictionaries with phenotype information
    phenotype_terms=list,  # List of dictionaries with phenotype information
    pipeline_version=str,  # Path to the pipeline executable versions report file
    rank_model_url=str,
    rank_model_version=str,
    rank_score_threshold=int,  # default: 8
    rerun_requested=bool,  # default: False
    reference_info=str,  # Path to the pipeline reference files versions report file
    research_requested=bool,  # default: False
    RNAfusion_inspector=str,  # Path to the RNA fusion inspector file
    RNAfusion_inspector_research=str,  # Path to the research RNA fusion inspector file
    RNAfusion_report=str,  # Path to the RNA fusion report file
    RNAfusion_report_research=str,  # Path to the research RNA fusion report file
    smn_tsv=str,  # path to an SMN TSV file
    status=str,  # default: 'inactive', choices: STATUS
    suspects=list,  # List of variants referred by there _id
    sv_rank_model_url=str,
    sv_rank_model_version=str,
    synopsis=str,  # The synopsis is a text blob
    tags=list,  # list of status modifiers e.g. "provisional", "diagnostic", "carrier", "medical attention", "technical attention"
    track=str,  # "rare" or "cancer"
    updated_at=datetime,
    variant_stats=dict,  # Contains the number of variants of each type for this case
    vcf_files=dict,  # A dictionary with vcf files
)

# Pydantic models for type-safe case operations


class PhenotypeItem(BaseModel):
    """A phenotype reference with ID and feature description."""

    phenotype_id: str
    feature: str


class PanelInfo(BaseModel):
    """Gene panel information stored in case."""

    panel_id: str
    panel_name: str
    display_name: str
    version: str
    updated_at: datetime
    nr_genes: int
    is_default: bool = False


class Case(BaseModel):
    """Pydantic model representing a Case entity in the database.

    This comprehensive model ensures all fields are properly validated and typed
    before database insertion. It provides a single source of truth for case structure.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )

    # Database ID (MongoDB uses '_id', aliased as 'case_id' for input)
    case_id: str = Field(alias="_id")

    # Display and metadata
    display_name: str
    owner: str  # institute_id
    collaborators: List[str] = Field(default_factory=list)
    assignees: Optional[List[str]] = Field(default_factory=list, alias="assignee")

    # Timestamps
    created_at: datetime
    updated_at: datetime
    scout_load_version: str
    analysis_date: Optional[datetime] = None

    # Case status and tracking
    status: Optional[str] = "inactive"
    is_research: bool = False
    research_requested: bool = False
    rerun_requested: bool = False
    lims_id: str = ""
    synopsis: str = ""

    # Genome and analysis info
    genome_build: str = "37"
    rna_genome_build: str = "38"
    track: str = "rare"  # "rare" or "cancer"

    # Individuals/samples
    individuals: List[Dict[str, Any]] = Field(default_factory=list)

    # Gene panels
    panels: List[Union[Dict[str, Any], PanelInfo]] = Field(default_factory=list)
    dynamic_gene_list: List[str] = Field(default_factory=list)

    # Phenotype information
    phenotype_terms: List[PhenotypeItem] = Field(default_factory=list)
    phenotype_groups: List[Dict[str, Any]] = Field(default_factory=list)

    # Variants and causatives
    suspects: List[str] = Field(default_factory=list)
    causatives: List[str] = Field(default_factory=list)

    # VCF and omics files
    vcf_files: Dict[str, Optional[str]] = Field(default_factory=dict)
    omics_files: Dict[str, Optional[str]] = Field(default_factory=dict)

    # Quality control and reports
    madeline_info: Optional[str] = None
    custom_images: Optional[Dict[str, Any]] = None
    delivery_report: Optional[str] = None
    rna_delivery_report: Optional[str] = None
    cnv_report: Optional[str] = None
    coverage_qc_report: Optional[str] = None
    multiqc: Optional[str] = None
    multiqc_rna: Optional[str] = None

    # Gene fusion reports
    gene_fusion_report: Optional[str] = None
    gene_fusion_report_research: Optional[str] = None
    RNAfusion_inspector: Optional[str] = None
    RNAfusion_inspector_research: Optional[str] = None
    RNAfusion_report: Optional[str] = None
    RNAfusion_report_research: Optional[str] = None

    # Ranking and filtering
    rank_model_version: Optional[str] = None
    rank_model_url: Optional[str] = None
    rank_score_threshold: Optional[float] = None
    sv_rank_model_version: Optional[str] = None
    sv_rank_model_url: Optional[str] = None

    # Diagnosis information
    diagnosis_genes: List[Dict[str, Any]] = Field(default_factory=list)
    diagnosis_phenotypes: List[Dict[str, Any]] = Field(default_factory=list)

    # Special analyses
    has_svvariants: bool = False
    has_strvariants: bool = False
    has_meivariants: bool = False
    has_outliers: bool = False
    has_methylation: bool = False

    # Data sources
    cohorts: List[str] = Field(default_factory=list)
    group: List[str] = Field(default_factory=list)
    paraphrase: Optional[str] = None
    smn_tsv: Optional[str] = None

    # Migration and tracking
    is_migrated: bool = False
    pipeline_version: Optional[str] = None

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, status):
        """Ensure status is one of allowed values."""
        if not status or status not in CASE_STATUSES:
            if status:
                logger.warning(f"Status '{status}' not in allowed statuses, setting to 'inactive'")
            return "inactive"
        return status

    @field_validator("genome_build")
    @classmethod
    def validate_genome_build(cls, build):
        """Ensure genome build is valid."""
        if build not in ["37", "38"]:
            logger.warning(f"Genome build '{build}' not valid, using '37'")
            return "37"
        return str(build)

    @field_validator("rna_genome_build")
    @classmethod
    def validate_rna_genome_build(cls, build):
        """Ensure RNA genome build is valid."""
        if build not in ["37", "38"]:
            logger.warning(f"RNA genome build '{build}' not valid, using '38'")
            return "38"
        return str(build)

    @field_validator("track")
    @classmethod
    def validate_track(cls, track):
        """Ensure track is valid."""
        if track not in ["rare", "cancer"]:
            logger.warning(f"Track '{track}' not valid, using 'rare'")
            return "rare"
        return track

    @field_validator("assignees", mode="before")
    @classmethod
    def validate_assignees(cls, v):
        """Convert string assignee to list if needed."""
        if isinstance(v, str):
            return [v]
        return v or []

    @model_validator(mode="before")
    def ensure_id_consistency(cls, values):
        """Ensure case_id or _id is set."""
        if "case_id" not in values and "_id" in values:
            values["case_id"] = values["_id"]
        elif "_id" not in values and "case_id" in values:
            values["_id"] = values["case_id"]
        return values

    @model_validator(mode="before")
    def normalize_list_fields(cls, values):
        """Convert None values to empty lists for collection fields.

        This ensures that list/dict fields never contain None, making them safe to
        iterate over or check length without guards throughout the codebase.
        """
        list_fields = [
            "phenotype_terms",
            "phenotype_groups",
            "suspects",
            "causatives",
            "diagnosis_genes",
            "diagnosis_phenotypes",
            "cohorts",
            "group",
        ]
        for field in list_fields:
            if field in values and values[field] is None:
                values[field] = []
        return values

    def to_dict(self) -> dict:
        """Convert model to dictionary for database insertion."""
        # Use by_alias=True to get '_id' instead of 'case_id' in output
        data = self.model_dump(by_alias=True, exclude_none=False)
        return data

    def to_db_format(self) -> dict:
        """Alias for to_dict() for clarity when preparing for database insertion."""
        return self.to_dict()

    def build_individuals(self, adapter, individuals_data: List[dict]) -> None:
        """Build and validate individuals for the case.

        Args:
            adapter: Database adapter for validation
            individuals_data: List of individual dictionaries
        """
        from scout.models.individual import Individual

        ind_objs = []
        for individual_data in individuals_data:
            individual = Individual(**individual_data)
            ind_objs.append(individual.to_dict())

        # Sort individuals by phenotype (affected first)
        self.individuals = sorted(ind_objs, key=lambda ind: -ind["phenotype"])

    def populate_panels(
        self, adapter, gene_panels: List[str], default_panels: List[str] = None
    ) -> None:
        """Populate and validate gene panels for the case.

        Args:
            adapter: Database adapter for panel lookup
            gene_panels: List of panel names
            default_panels: List of default panel names
        """
        if default_panels is None:
            default_panels = []

        panels = []
        for panel_name in gene_panels:
            panel_obj = adapter.gene_panel(panel_name)
            if not panel_obj:
                logger.warning(
                    f"Panel {panel_name} does not exist in database and will not be saved."
                )
                continue

            panel = {
                "panel_id": panel_obj["_id"],
                "panel_name": panel_obj["panel_name"],
                "display_name": panel_obj["display_name"],
                "version": panel_obj["version"],
                "updated_at": panel_obj["date"],
                "nr_genes": len(panel_obj["genes"]),
                "is_default": panel_name in default_panels,
            }
            panels.append(panel)

        self.panels = panels
        self.dynamic_gene_list = []

    def populate_phenotypes(self, adapter, phenotype_terms: List[str] = None) -> None:
        """Populate and validate phenotype terms for the case.

        Args:
            adapter: Database adapter for HPO term lookup
            phenotype_terms: List of HPO term IDs
        """
        if not phenotype_terms:
            self.phenotype_terms = []
            return

        phenotypes = []
        for phenotype_id in phenotype_terms:
            phenotype_obj = adapter.hpo_term(phenotype_id)
            if phenotype_obj is None:
                logger.warning(f"HPO term '{phenotype_id}' not found in database, skipping.")
                continue

            phenotypes.append(
                PhenotypeItem(
                    phenotype_id=phenotype_id,
                    feature=phenotype_obj.get("description"),
                )
            )

        self.phenotype_terms = phenotypes if phenotypes else []

    def set_phenotype_groups(
        self, adapter, phenotype_groups: List[str], institute_obj: dict, institute_id: str
    ) -> None:
        """Set and validate phenotype groups for the case.

        Args:
            adapter: Database adapter for term lookup
            phenotype_groups: List of phenotype group names
            institute_obj: Institute object from database
            institute_id: Institute ID
        """
        if not phenotype_groups:
            self.phenotype_groups = []
            return

        groups = []
        institute_phenotype_groups = set(PHENOTYPE_GROUPS.keys())
        if institute_obj.get("phenotype_groups"):
            institute_phenotype_groups.update(institute_obj.get("phenotype_groups").keys())

        for phenotype in phenotype_groups:
            if phenotype not in institute_phenotype_groups:
                logger.warning(
                    f"Phenotype group '{phenotype}' not found for institute '{institute_id}'."
                )
                continue

            phenotype_obj = self._build_phenotype(adapter, phenotype)
            if phenotype_obj:
                groups.append(phenotype_obj)
            else:
                logger.warning(f"Could not find phenotype group '{phenotype}' in term collection.")

        self.phenotype_groups = groups if groups else []

    def set_cohorts(self, adapter, cohorts: List[str], institute_obj: dict) -> None:
        """Set and validate cohorts for the case.

        Args:
            adapter: Database adapter
            cohorts: List of cohort names
            institute_obj: Institute object from database
        """
        if not cohorts:
            self.cohorts = []
            return

        self.cohorts = cohorts

        # Check if all case cohorts are registered under the institute
        institute_cohorts = set(institute_obj.get("cohorts", []))
        all_cohorts = institute_cohorts.union(set(cohorts))
        if len(all_cohorts) > len(institute_cohorts):
            logger.warning("Updating institute with new cohort terms")
            adapter.institute_collection.find_one_and_update(
                {"_id": institute_obj["_id"]}, {"$set": {"cohorts": list(all_cohorts)}}
            )

    def populate_variant_flags(self) -> None:
        """Populate variant type flags based on VCF and omics files."""
        self.has_svvariants = bool(
            self.vcf_files.get("vcf_sv") or self.vcf_files.get("vcf_sv_research")
        )
        self.has_strvariants = bool(self.vcf_files.get("vcf_str"))
        self.has_meivariants = bool(self.vcf_files.get("vcf_mei"))
        self.has_outliers = bool(
            self.omics_files.get("fraser")
            or self.omics_files.get("outrider")
            or self.omics_files.get("methbat")
        )
        self.has_methylation = bool(self.omics_files.get("methbat"))

    def _build_phenotype(self, adapter, phenotype_id: str) -> Dict[str, str]:
        """Build a phenotype object from HPO term.

        Args:
            adapter: Database adapter
            phenotype_id: HPO term ID

        Returns:
            dict with phenotype_id and feature
        """
        phenotype_obj = {}
        phenotype = adapter.hpo_term(phenotype_id)
        if phenotype:
            phenotype_obj["phenotype_id"] = phenotype["hpo_id"]
            phenotype_obj["feature"] = phenotype["description"]
        return phenotype_obj
