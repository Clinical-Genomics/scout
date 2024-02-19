from __future__ import absolute_import

import logging
from datetime import datetime

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
    splice_junctions_bed=str,  # An indexed junctions .bed.gz file obtained from STAR v2 aligner *.SJ.out.tab file.
    predicted_ancestry=str,  # one of AFR AMR EAS EUR SAS UNKNOWN
    tumor_type=str,
    tmb=str,
    msi=str,
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
