from __future__ import absolute_import

import logging
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from scout.build import build_individual
from scout.exceptions import ConfigError, IntegrityError

logger = logging.getLogger(__name__)

"""
individual = dict(
    individual_id=str,  # required
    display_name=str,
    sex=str,
    phenotype=int, # not really int - str in db
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
    sv_rank_model_version=str,
    synopsis=str,  # The synopsis is a text blob
    tags=list,  # list of status modifiers e.g. "provisional", "diagnostic", "carrier", "medical attention", "technical attention"
    track=str,  # "rare" or "cancer"
    updated_at=datetime,
    variant_stats=dict,  # Contains the number of variants of each type for this case
    vcf_files=dict,  # A dictionary with vcf files
)
"""


class FSHDLocus(BaseModel):
    mapid: str
    chromosome: str
    haplotype: str
    count: str
    spanning_coverage: str


class PhenotypeTerm(BaseModel):
    phenotype_id: str
    feature: Optional[str] = None


class PhenotypeGroup(BaseModel):
    phenotype_id: str
    label: Optional[str] = None


class IndividualModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    individual_id: str
    display_name: Optional[str] = None
    sex: Optional[str] = None
    phenotype: str = "unknown"

    father: Optional[str] = None
    mother: Optional[str] = None

    capture_kits: List[str] = Field(default_factory=list)

    bam_file: Optional[str] = None
    minor_allele_frequency_wig: Optional[str] = None
    rhocall_bed: Optional[str] = None
    rhocall_wig: Optional[str] = None
    tiddit_coverage_wig: Optional[str] = None
    upd_regions_bed: Optional[str] = None
    upd_sites_bed: Optional[str] = None
    vcf2cytosure: Optional[str] = None

    analysis_type: Optional[str] = None

    confirmed_sex: Optional[bool] = None
    confirmed_parent: Optional[bool] = None

    is_sma: Optional[bool] = None
    is_sma_carrier: Optional[bool] = None

    smn1_cn: Optional[int] = None
    smn2_cn: Optional[int] = None
    smn2delta78_cn: Optional[int] = None
    smn_27134_cn: Optional[int] = None

    rna_alignment_path: Optional[str] = None
    rna_coverage_bigwig: Optional[str] = None
    omics_sample_id: Optional[str] = None

    splice_junctions_bed: Optional[str] = None
    predicted_ancestry: Optional[str] = None

    tumor_type: Optional[str] = None
    tmb: Optional[str] = None
    msi: Optional[str] = None
    hrd: Optional[str] = None
    tumor_purity: Optional[float] = None
    tissue_type: Optional[str] = None

    chromograph_images: Optional[str] = None
    fshd_loci: List[FSHDLocus] = Field(default_factory=list)


class PanelModel(BaseModel):
    panel_id: str
    panel_name: str
    display_name: str
    version: str
    updated_at: datetime
    nr_genes: int
    is_default: bool = False


class CaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    case_id: str = Field(alias="_id")
    display_name: str

    owner: str
    collaborators: List[str]

    assignees: List[str] = Field(default_factory=list)

    individuals: List[IndividualModel] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    suspects: List[str] = Field(default_factory=list)
    causatives: List[str] = Field(default_factory=list)

    synopsis: str = ""
    status: str = "inactive"

    is_research: bool = False
    research_requested: bool = False
    rerun_requested: bool = False

    cohorts: List[str] = Field(default_factory=list)

    analysis_date: Optional[datetime] = None

    panels: List[PanelModel] = Field(default_factory=list)

    dynamic_gene_list: List[str] = Field(default_factory=list)

    genome_build: str = "37"
    rna_genome_build: str = "38"

    rank_model_version: Optional[str] = None
    sv_rank_model_version: Optional[str] = None
    rank_score_threshold: Optional[float] = None

    phenotype_terms: List[PhenotypeTerm] = Field(default_factory=list)
    phenotype_groups: List[PhenotypeGroup] = Field(default_factory=list)

    madeline_info: Optional[str] = None

    vcf_files: Dict = Field(default_factory=dict)
    omics_files: Dict = Field(default_factory=dict)

    has_svvariants: bool = False
    has_strvariants: bool = False
    has_meivariants: bool = False
    has_outliers: bool = False
    has_methylation: bool = False

    is_migrated: bool = False

    track: str = "rare"
    group: List[str] = Field(default_factory=list)

    @field_validator("genome_build")
    def validate_build(cls, v):
        if v not in {"37", "38"}:
            raise ValueError("Genome build must be 37 or 38")
        return v


class CaseFactory:

    @staticmethod
    def build(case_data: dict, adapter) -> CaseModel:
        now = datetime.now()

        # ---- Owner validation ----
        institute_id = case_data.get("owner")
        if not institute_id:
            raise ConfigError("Case has to have a institute")

        institute_obj = adapter.institute(institute_id)
        if not institute_obj:
            raise IntegrityError(f"Institute {institute_id} not found")

        # ---- Collaborators ----
        collaborators = set(case_data.get("collaborators", []))
        collaborators.add(institute_id)

        # ---- Individuals ----
        individuals = []

        for individual in case_data.get("individuals", []):
            built = build_individual(individual)
            validated = IndividualModel.model_validate(built)
            individuals.append(validated)

        individuals.sort(key=lambda ind: -ind.phenotype)

        # ---- Panels ----
        panels = []
        default_panels = set(case_data.get("default_panels", []))

        for panel_name in case_data.get("gene_panels", []):
            panel_obj = adapter.gene_panel(panel_name)
            if not panel_obj:
                continue

            panels.append(
                PanelModel(
                    panel_id=panel_obj["_id"],
                    panel_name=panel_obj["panel_name"],
                    display_name=panel_obj["display_name"],
                    version=panel_obj["version"],
                    updated_at=panel_obj["date"],
                    nr_genes=len(panel_obj["genes"]),
                    is_default=panel_name in default_panels,
                )
            )

        # ---- Construct case ----
        case = CaseModel(
            case_id=case_data["case_id"],
            display_name=case_data.get("display_name", case_data["case_id"]),
            owner=institute_id,
            collaborators=list(collaborators),
            assignees=[case_data["assignee"]] if case_data.get("assignee") else [],
            individuals=individuals,
            created_at=now,
            updated_at=now,
            analysis_date=case_data.get("analysis_date", now),
            synopsis=case_data.get("synopsis", ""),
            status=case_data.get("status") or "inactive",
            genome_build=case_data.get("genome_build", "37"),
            rna_genome_build=case_data.get("rna_genome_build", "38"),
            rank_model_version=case_data.get("rank_model_version"),
            sv_rank_model_version=case_data.get("sv_rank_model_version"),
            rank_score_threshold=case_data.get("rank_score_threshold"),
            suspects=case_data.get("suspects", []),
            causatives=case_data.get("causatives", []),
            panels=panels,
            vcf_files=case_data.get("vcf_files", {}),
            omics_files=case_data.get("omics_files", {}),
            track=case_data.get("track", "rare"),
            group=case_data.get("group", []),
        )

        @computed_field
        @property
        def has_svvariants(self) -> bool:
            return bool(self.vcf_files.get("vcf_sv") or self.vcf_files.get("vcf_sv_research"))

        @computed_field
        @property
        def has_strvariants(self) -> bool:
            return bool(self.vcf_files.get("vcf_str"))

        @computed_field
        @property
        def has_meivariants(self) -> bool:
            return bool(self.vcf_files.get("vcf_mei"))

        @computed_field
        @property
        def has_outliers(self) -> bool:
            return bool(
                self.omics_files.get("fraser")
                or self.omics_files.get("outrider")
                or self.omics_files.get("methbat")
            )

        @computed_field
        @property
        def has_methylation(self) -> bool:
            return bool(self.omics_files.get("methbat"))

        return case
