from __future__ import absolute_import

import os
import logging
from datetime import datetime

from . import STATUS
from .individual import Individual

from scout.models import PhenotypeTerm
from scout.models.panel import GenePanel
from scout.constants import ANALYSIS_TYPES

logger = logging.getLogger(__name__)

individual = dict(
    individual_id=str,  # required
    display_name=str,
    sex=str,
    phenotype=int,
    father=str,  # Individual id of father
    mother=str,  # Individual id of mother
    capture_kits=list,  # List of names of capture kits
    bam_file=str,  # Path to bam file
    rhocall_bed=str,  # Path to bed file
    rhocall_wig=str,  # Path to wig file
    tiddit_coverage_wig=str,  # Path to wig file
    upd_regions_bed=str,  # Path to bed file
    upd_sites_bed=str,  # Path to bed file
    vcf2cytosure=str,  # Path to CGH file
    analysis_type=str,  # choices=ANALYSIS_TYPES
    confirmed_sex=bool,  # True or False. None if no check has been done
    confirmed_parent=bool,
    is_sma=bool,  # True / False if SMA status determined - None if not done.
    is_sma_carrier=bool,  # True / False if SMA carriership determined - None if not done.
    smn1_cn=int,  # CopyNumber
    smn2_cn=int,  # CopyNumber
    smn2delta78_cn=int,  # CopyNumber
    smn_27134_cn=int,  # CopyNumber
    predicted_ancestry=str,  # one of AFR AMR EAS EUR SAS UNKNOWN
    tumor_type=str,
    tmb=str,
    msi=str,
    tumor_purity=float,
    tissue_type=str,
    chromograph_images=str,  # path to image files
)

case = dict(
    # This is a string with the id for the family:
    case_id=str,  # required=True, unique
    # This is the string that will be shown in scout:
    display_name=str,  # required
    # This internal_id for the owner of the case. E.g. 'cust000'
    owner=str,  # required
    # These are the names of all the collaborators that are allowed to view the
    # case, including the owner
    collaborators=list,  # List of institute_ids
    assignees=list,  # list of str _id of a user (email)
    individuals=list,  # list of dictionaries with individuals
    created_at=datetime,
    updated_at=datetime,
    suspects=list,  # List of variants referred by there _id
    causatives=list,  # List of variants referred by there _id
    synopsis=str,  # The synopsis is a text blob
    status=str,  # default='inactive', choices=STATUS
    is_research=bool,  # default=False
    research_requested=bool,  # default=False
    rerun_requested=bool,  # default=False
    analysis_date=datetime,
    # default_panels specifies which panels that should be shown when
    # the case is opened
    panels=list,  # list of dictionaries with panel information
    dynamic_gene_list=list,  # List of genes
    genome_build=str,  # This should be 37 or 38
    genome_version=float,  # What version of the build
    rank_model_version=str,
    rank_score_threshold=int,  # default=8
    sv_rank_model_version=str,
    phenotype_terms=list,  # List of dictionaries with phenotype information
    phenotype_groups=list,  # List of dictionaries with phenotype information
    madeline_info=str,  # madeline info is a full xml file
    delivery_report=str,  # delivery report is a path to html file
    cnv_report=str,  # CNV report is a path to pdf file
    coverage_qc_report=str,  # Covearge and qc report is a path to a html file
    vcf_files=dict,  # A dictionary with vcf files
    smn_tsv=str,  # path to an SMN TSV file
    diagnosis_phenotypes=list,  # List of references to diseases
    diagnosis_genes=list,  # List of references to genes
    has_svvariants=bool,  # default=False
    has_strvariants=bool,  # default=False
    is_migrated=bool,  # default=False
    multiqc=str,  # path to multiqc report
    group=list,  # a list of group ids for cases conceptually grouped together with this
)
