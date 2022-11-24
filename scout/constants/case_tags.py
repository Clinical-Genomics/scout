ANALYSIS_TYPES = ("wgs", "wes", "mixed", "unknown", "panel", "panel-umi", "external")

# keys are used in the load report cli, while key_name is saved in case database documents
CUSTOM_CASE_REPORTS = {
    "delivery": {"key_name": "delivery_report", "format": "HTML", "pdf_export": True},
    "cnv": {"key_name": "cnv_report", "format": "PDF", "pdf_export": False},
    "cov_qc": {"key_name": "coverage_qc_report", "format": "HTML", "pdf_export": True},
    "exe_ver": {"key_name": "pipeline_version", "format": "YAML", "pdf_export": True},
    "multiqc": {"key_name": "multiqc", "format": "HTML", "pdf_export": False},
    "multiqc_rna": {"key_name": "multiqc_rna", "format": "HTML", "pdf_export": False},
    "gene_fusion": {"key_name": "gene_fusion_report", "format": "PDF", "pdf_export": False},
    "gene_fusion_research": {
        "key_name": "gene_fusion_report_research",
        "format": "PDF",
        "pdf_export": False,
    },
    "reference_info": {"key_name": "reference_info", "format": "YAML", "pdf_export": True},
}

CASE_REPORT_CASE_FEATURES = [
    "display_name",
    "created_at",
    "updated_at",
    "status",
    "madeline_info",
    "synopsis",
    "phenotype_terms",
    "diagnosis_phenotypes",
    "panels",
]

CASE_REPORT_CASE_IND_FEATURES = [
    "display_name",
    "sex",
    "confirmed_sex",
    "phenotype",
    "phenotype_human",
    "analysis_type",
    "predicted_ancestry",
    "confirmed_parent",
]

CASE_REPORT_VARIANT_TYPES = {
    "causatives_detailed": "causatives",
    "partial_causatives_detailed": "partial_causatives",
    "suspects_detailed": "suspects",
    "classified_detailed": "acmg_classification",
    "tagged_detailed": "manual_rank",
    "tier_detailed": "cancer_tier",
    "dismissed_detailed": "dismiss_variant",
    "commented_detailed": "is_commented",
}

SEX_MAP = {
    1: "male",
    2: "female",
    "other": "unknown",
    0: "unknown",
    "1": "male",
    "2": "female",
    "0": "unknown",
}
REV_SEX_MAP = {"male": "1", "female": "2", "unknown": "0"}

PHENOTYPE_MAP = {1: "unaffected", 2: "affected", 0: "unknown", -9: "unknown"}
CANCER_PHENOTYPE_MAP = {1: "normal", 2: "tumor", 0: "unknown", -9: "unknown"}
REV_PHENOTYPE_MAP = {value: key for key, value in PHENOTYPE_MAP.items()}

CASE_STATUSES = ("prioritized", "inactive", "active", "solved", "archived", "ignored")

VERBS_MAP = {
    "assign": "was assigned to",
    "unassign": "was unassigned from",
    "status": "updated the status for",
    "comment": "commented on",
    "comment_update": "updated a comment for",
    "synopsis": "updated synopsis for",
    "pin": "pinned variant",
    "unpin": "removed pinned variant",
    "sanger": "ordered sanger sequencing for",
    "cancel_sanger": "cancelled sanger order for",
    "archive": "archived",
    "open_research": "opened research mode for",
    "reset_research": "canceled research mode request for",
    "mark_causative": "marked causative for",
    "unmark_causative": "unmarked causative for",
    "mark_partial_causative": "mark partial causative for",
    "unmark_partial_causative": "unmarked partial causative for",
    "manual_rank": "updated manual rank for",
    "cancer_tier": "updated cancer tier for",
    "add_phenotype": "added HPO term for",
    "remove_phenotype": "removed HPO term for",
    "remove_variants": "removed variants for",
    "add_case": "added case",
    "update_case": "updated case",
    "update_individual": "updated individuals for",
    "check_case": "marked case as",
    "share": "shared case with",
    "unshare": "revoked access for",
    "rerun": "requested rerun of",
    "rerun_reset": "canceled rerun of",
    "rerun_monitor": "requested rerun monitoring for",
    "rerun_unmonitor": "disabled rerun monitoring for",
    "validate": "marked validation status for",
    "update_diagnosis": "updated diagnosis for",
    "add_cohort": "updated cohort for",
    "remove_cohort": "removed cohort for",
    "acmg": "updated ACMG classification for",
    "dismiss_variant": "dismissed variant for",
    "reset_dismiss_variant": "reset dismissed variant status for",
    "reset_dismiss_all_variants": "reset all dismissed variants for",
    "mosaic_tags": "updated mosaic tags for",
    "update_default_panels": "updated default panels for",
    "update_clinical_filter_hpo": "updated clinical filter HPO status for",
    "mme_add": "exported to Matchmaker patient",
    "mme_remove": "removed from Matchmaker patient",
    "beacon_add": "exported variants to the Beacon",
    "beacon_remove": "removed variants from the Beacon",
    "filter_stash": "stored a filter for",
    "filter_audit": "marked case audited with filter",
    "update_sample": "updated sample data for",
    "update_case_group_ids": "updated case group ids for",
}

# Font-awesome jcons used by VERBS_ICONS_MAP
ICON_TIMES = "icon fas fa-times"
ICON_FOLDER_OPEN = "icon fas fa-folder-open"
ICON_SEARCH = "icon fas fa-search"
ICON_RANK = "icon fa fa-check-double"
ICON_GEARS = "icon fas fa-gears"
ICON_SHARE = "icon fas fa-share"

VERBS_ICONS_MAP = {
    "assign": "icon fas fa-heart",
    "unassign": ICON_TIMES,
    "status": "icon fas fa-star",
    "comment": "icon fas fa-comment",
    "comment_update": "icon fas fa-comment",
    "synopsis": ICON_FOLDER_OPEN,
    "pin": "icon fas fa-map-pin",
    "unpin": "icon fas fa-map-pin",
    "sanger": "icon fas fa-check",
    "cancel_sanger": ICON_TIMES,
    "archive": "icon fas fa-archive",
    "open_research": ICON_SEARCH,
    "reset_research": ICON_SEARCH,
    "mark_causative": ICON_RANK,
    "unmark_causative": ICON_RANK,
    "mark_partial_causative": ICON_RANK,
    "unmark_partial_causative": ICON_RANK,
    "manual_rank": ICON_RANK,
    "cancer_tier": ICON_RANK,
    "add_phenotype": ICON_FOLDER_OPEN,
    "remove_phenotype": ICON_FOLDER_OPEN,
    "add_case": ICON_FOLDER_OPEN,
    "update_case": "icon fas fa-folder-open",
    "update_individual": ICON_FOLDER_OPEN,
    "check_case": "icon fas fa-star",
    "share": ICON_SHARE,
    "unshare": ICON_TIMES,
    "rerun": ICON_GEARS,
    "rerun_monitor": ICON_GEARS,
    "rerun_unmonitor": ICON_GEARS,
    "validate": "icon fas fa-check",
    "update_diagnosis": ICON_FOLDER_OPEN,
    "add_cohort": ICON_FOLDER_OPEN,
    "remove_cohort": ICON_FOLDER_OPEN,
    "acmg": ICON_RANK,
    "dismiss_variant": ICON_TIMES,
    "reset_dismiss_variant": ICON_TIMES,
    "reset_dismiss_all_variants": ICON_TIMES,
    "mosaic_tags": ICON_RANK,
    "update_default_panels": ICON_FOLDER_OPEN,
    "update_clinical_filter_hpo": ICON_FOLDER_OPEN,
    "mme_add": ICON_SHARE,
    "mme_remove": ICON_TIMES,
    "beacon_add": ICON_SHARE,
    "beacon_remove": ICON_TIMES,
    "filter_stash": ICON_SEARCH,
    "filter_audit": ICON_SEARCH,
    "update_sample": ICON_FOLDER_OPEN,
    "update_case_group_ids": ICON_FOLDER_OPEN,
}

# Tissue types for rare disease samples and controls

SOURCES = [
    "blood",
    "bone marrow",
    "buccal swab",
    "cell line",
    "cell-free DNA",
    "cytology (FFPE)",
    "cytology (not fixed/fresh)",
    "muscle",
    "nail",
    "saliva",
    "skin",
    "tissue (FFPE)",
    "tissue (fresh frozen)",
    "CVB",
    "AC",
    "other fetal tissue",
    "other",
    "unknown",
]

SAMPLE_SOURCE = dict((i, el) for i, el in enumerate(SOURCES))

CASE_SEARCH_TERMS = {
    "case": {"label": "Case or Individual Name", "prefix": "case:", "placeholder": "example:18201"},
    "exact_pheno": {
        "label": "HPO Terms",
        "prefix": "exact_pheno:",
        "placeholder": "example:HP:0001166,HP:0001250,...",
    },
    "exact_dia": {
        "label": "OMIM Terms",
        "prefix": "exact_dia:",
        "placeholder": "example:OMIM:616538,OMIM:607681,...",
    },
    "synopsis": {
        "label": "Search Synopsis",
        "prefix": "synopsis:",
        "placeholder": "example:epilepsy",
    },
    "panel": {"label": "Gene Panel", "prefix": "panel:", "placeholder": "example:NMD"},
    "status": {"label": "Case Status", "prefix": "status:", "placeholder": "example:active"},
    "track": {"label": "Analysis Track", "prefix": "track:", "placeholder": "rare or cancer"},
    "pheno_group": {
        "label": "Phenotype Group",
        "prefix": "pheno_group:",
        "placeholder": "example:HP:0001166",
    },
    "cohort": {"label": "Patient Cohort", "prefix": "cohort:", "placeholder": "example:pedhep"},
    "similar_case": {
        "label": "Similar Case",
        "prefix": "similar_case:",
        "placeholder": "example:18201",
    },
    "similar_pheno": {
        "label": "Similar Phenotype",
        "prefix": "similar_pheno:",
        "placeholder": "example:HP:0001166,HP:0001250,..",
    },
    "pinned": {"label": "Pinned Gene", "prefix": "pinned:", "placeholder": "example:POT1"},
    "causative": {"label": "Causative Gene", "prefix": "causative:", "placeholder": "example:POT1"},
    "user": {
        "label": "Assigned User",
        "prefix": "user:",
        "placeholder": "example:John Doe",
    },
}
